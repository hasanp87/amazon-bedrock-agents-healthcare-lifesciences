"""
SOP Loader for loading SOPs from various sources
Uses strands-agents-sops library for markdown-based SOP loading
"""

import json
import yaml
import re
from pathlib import Path
from typing import List, Dict, Optional
from .sop_models import SOP, SOPStep, SOPMetadata, SOPRepository

# Import from strands-agents-sops library
try:
    from strands_sops import load_sop_from_file, load_sops_from_directory
    from strands_sops import parse_sop_markdown
    LIBRARY_AVAILABLE = True
    print("✅ Using strands_sops library for SOP loading")
except ImportError:
    LIBRARY_AVAILABLE = False
    print("⚠️ Warning: strands_sops library not available, using fallback implementation")


class SOPLoader:
    """
    Loads SOPs from various sources using strands-agents-sops library
    
    This loader prioritizes using the strands-agents-sops library functions
    for loading markdown-based SOPs with RFC 2119 keywords. It also maintains
    backward compatibility with legacy JSON/YAML formats.
    """
    
    def __init__(self):
        self.repositories: Dict[str, SOPRepository] = {}
    
    def load_from_directory(self, directory_path: str, repository_name: str = "local") -> SOPRepository:
        """
        Load all SOPs from a directory using strands-agents-sops library
        
        This method uses the library's built-in directory loading functionality
        for markdown files, while maintaining support for legacy JSON/YAML formats.
        
        Args:
            directory_path: Path to directory containing SOP files
            repository_name: Name for the repository
            
        Returns:
            SOPRepository with loaded SOPs
        """
        path = Path(directory_path)
        
        if not path.exists():
            raise ValueError(f"Directory not found: {directory_path}")
        
        repository = SOPRepository(
            name=repository_name,
            description=f"SOPs loaded from {directory_path}",
            source_type="local",
            source_url=str(path.absolute())
        )
        
        # Use library function for markdown SOPs if available
        if LIBRARY_AVAILABLE:
            try:
                # Load all markdown SOPs using library function
                library_sops = load_sops_from_directory(str(path))
                for lib_sop in library_sops:
                    # Convert library SOP to our SOP model if needed
                    sop = self._convert_library_sop(lib_sop)
                    repository.add_sop(sop)
                    print(f"✓ Loaded SOP: {sop.id} from markdown (using strands_sops library)")
            except Exception as e:
                print(f"⚠️ Library loading failed, falling back to custom parser: {e}")
                self._load_markdown_files_fallback(path, repository)
        else:
            # Fallback to custom markdown parsing
            self._load_markdown_files_fallback(path, repository)
        
        # Load legacy JSON files
        for json_file in path.glob("*.json"):
            try:
                sop = self._load_sop_from_json(json_file)
                repository.add_sop(sop)
                print(f"✓ Loaded SOP: {sop.id} from {json_file.name} (JSON format)")
            except Exception as e:
                print(f"✗ Error loading {json_file.name}: {e}")
        
        # Load legacy YAML files
        for yaml_file in list(path.glob("*.yaml")) + list(path.glob("*.yml")):
            try:
                sop = self._load_sop_from_yaml(yaml_file)
                repository.add_sop(sop)
                print(f"✓ Loaded SOP: {sop.id} from {yaml_file.name} (YAML format)")
            except Exception as e:
                print(f"✗ Error loading {yaml_file.name}: {e}")
        
        self.repositories[repository_name] = repository
        return repository
    
    def load_sop_from_file(self, file_path: str) -> SOP:
        """
        Load a single SOP from a file using strands-agents-sops library
        
        This method uses the library's built-in file loading functionality.
        
        Args:
            file_path: Path to SOP file (markdown, JSON, or YAML)
            
        Returns:
            Loaded SOP object
        """
        path = Path(file_path)
        
        if not path.exists():
            raise ValueError(f"File not found: {file_path}")
        
        # Use library function for markdown files
        if path.suffix == '.md' and LIBRARY_AVAILABLE:
            try:
                lib_sop = load_sop_from_file(str(path))
                return self._convert_library_sop(lib_sop)
            except Exception as e:
                print(f"⚠️ Library loading failed for {file_path}, using fallback: {e}")
                return self._load_sop_from_markdown_fallback(path)
        elif path.suffix == '.md':
            return self._load_sop_from_markdown_fallback(path)
        elif path.suffix == '.json':
            return self._load_sop_from_json(path)
        elif path.suffix in ['.yaml', '.yml']:
            return self._load_sop_from_yaml(path)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")
    
    def _convert_library_sop(self, lib_sop) -> SOP:
        """
        Convert a library SOP object to our SOP model
        
        Args:
            lib_sop: SOP object from strands_sops library
            
        Returns:
            Our SOP model instance
        """
        # If library SOP is already compatible, return as-is
        if isinstance(lib_sop, SOP):
            return lib_sop
        
        # Otherwise, convert library SOP attributes to our model
        # This handles cases where library SOP structure differs slightly
        steps = []
        if hasattr(lib_sop, 'steps'):
            for lib_step in lib_sop.steps:
                if not isinstance(lib_step, SOPStep):
                    # Convert library step to our SOPStep
                    step = SOPStep(
                        step_number=getattr(lib_step, 'step_number', getattr(lib_step, 'number', 0)),
                        description=getattr(lib_step, 'description', getattr(lib_step, 'title', '')),
                        details=getattr(lib_step, 'details', getattr(lib_step, 'content', None)),
                        required=getattr(lib_step, 'required', True),
                        validation_criteria=getattr(lib_step, 'validation_criteria', None),
                        estimated_time=getattr(lib_step, 'estimated_time', None),
                        warnings=getattr(lib_step, 'warnings', None)
                    )
                    steps.append(step)
                else:
                    steps.append(lib_step)
        
        # Convert metadata
        metadata = None
        if hasattr(lib_sop, 'metadata'):
            lib_meta = lib_sop.metadata
            if not isinstance(lib_meta, SOPMetadata):
                metadata = SOPMetadata(
                    version=getattr(lib_meta, 'version', '1.0'),
                    created_date=getattr(lib_meta, 'created_date', ''),
                    last_updated=getattr(lib_meta, 'last_updated', ''),
                    author=getattr(lib_meta, 'author', ''),
                    reviewer=getattr(lib_meta, 'reviewer', None),
                    approval_status=getattr(lib_meta, 'approval_status', 'draft'),
                    review_frequency=getattr(lib_meta, 'review_frequency', None)
                )
            else:
                metadata = lib_meta
        else:
            metadata = SOPMetadata(
                version='1.0',
                created_date='',
                last_updated='',
                author=''
            )
        
        # Create our SOP instance
        sop = SOP(
            id=getattr(lib_sop, 'id', getattr(lib_sop, 'sop_id', 'UNKNOWN')),
            title=getattr(lib_sop, 'title', ''),
            description=getattr(lib_sop, 'description', ''),
            category=getattr(lib_sop, 'category', 'operational'),
            priority=getattr(lib_sop, 'priority', 'medium'),
            steps=steps,
            metadata=metadata,
            applicable_departments=getattr(lib_sop, 'applicable_departments', []),
            applicable_roles=getattr(lib_sop, 'applicable_roles', []),
            keywords=getattr(lib_sop, 'keywords', []),
            prerequisites=getattr(lib_sop, 'prerequisites', None),
            related_sops=getattr(lib_sop, 'related_sops', None),
            references=getattr(lib_sop, 'references', None)
        )
        
        return sop
    
    def _load_markdown_files_fallback(self, path: Path, repository: SOPRepository):
        """Fallback method to load markdown files when library is not available"""
        for md_file in path.glob("*.md"):
            try:
                sop = self._load_sop_from_markdown_fallback(md_file)
                repository.add_sop(sop)
                print(f"✓ Loaded SOP: {sop.id} from {md_file.name} (fallback markdown parser)")
            except Exception as e:
                print(f"✗ Error loading {md_file.name}: {e}")
    
    def _load_sop_from_json(self, file_path: Path) -> SOP:
        """Load an SOP from a JSON file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return self._parse_sop_data(data)
    
    def _load_sop_from_yaml(self, file_path: Path) -> SOP:
        """Load an SOP from a YAML file"""
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        return self._parse_sop_data(data)
    
    def _load_sop_from_markdown_fallback(self, file_path: Path) -> SOP:
        """
        Fallback method to load an SOP from a Markdown file when library is unavailable
        
        This method parses markdown-based SOPs that use RFC 2119 keywords
        (MUST, SHOULD, MAY, etc.) for defining workflow requirements.
        
        Args:
            file_path: Path to markdown SOP file
            
        Returns:
            Parsed SOP object
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract metadata from front matter (between **key:** value pairs)
        metadata_pattern = r'\*\*([^*]+):\*\*\s*(.+?)(?=\*\*|\n\n|$)'
        metadata_matches = re.findall(metadata_pattern, content[:2000])  # Check first 2000 chars
        
        metadata_dict = {}
        for key, value in metadata_matches:
            metadata_dict[key.strip()] = value.strip()
        
        # Extract title (first # heading)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else file_path.stem
        
        # Parse metadata
        sop_id = metadata_dict.get('SOP ID', file_path.stem.upper())
        category = metadata_dict.get('Category', 'operational').lower()
        priority = metadata_dict.get('Priority', 'medium').lower()
        version = metadata_dict.get('Version', '1.0')
        last_updated = metadata_dict.get('Last Updated', '')
        
        # Parse applicable departments and roles
        applicable_departments = []
        if 'Applicable Departments' in metadata_dict:
            dept_str = metadata_dict['Applicable Departments']
            applicable_departments = [d.strip() for d in dept_str.split(',')]
        
        applicable_roles = []
        if 'Applicable Roles' in metadata_dict:
            roles_str = metadata_dict['Applicable Roles']
            applicable_roles = [r.strip() for r in roles_str.split(',')]
        
        # Extract overview/description
        overview_match = re.search(r'##\s+Overview\s+(.+?)(?=##|\Z)', content, re.DOTALL)
        description = overview_match.group(1).strip() if overview_match else title
        # Limit description to first paragraph
        description = description.split('\n\n')[0].strip()
        
        # Extract prerequisites
        prerequisites = []
        prereq_match = re.search(r'##\s+Prerequisites\s+(.+?)(?=##|\Z)', content, re.DOTALL)
        if prereq_match:
            prereq_content = prereq_match.group(1).strip()
            prereq_lines = [line.strip('- ').strip() for line in prereq_content.split('\n') if line.strip().startswith('-')]
            prerequisites = prereq_lines
        
        # Parse steps from markdown sections (### Step N: Title)
        steps = []
        step_pattern = r'###\s+Step\s+(\d+):\s+(.+?)\n\n\*\*Description:\*\*\s+(.+?)\n\n(.*?)(?=###\s+Step|\n##|\Z)'
        step_matches = re.findall(step_pattern, content, re.DOTALL)
        
        for step_num, step_title, step_desc, step_body in step_matches:
            step_number = int(step_num)
            
            # Parse the step body for RFC 2119 keywords and other information
            # Extract the detailed instructions (paragraphs starting with You MUST/SHOULD/MAY)
            details_lines = []
            for line in step_body.split('\n'):
                line = line.strip()
                if line.startswith('You MUST') or line.startswith('You SHOULD') or line.startswith('You MAY'):
                    details_lines.append(line)
            details = ' '.join(details_lines) if details_lines else step_desc
            
            # Extract validation criteria
            validation_criteria = []
            validation_match = re.search(r'\*\*Validation Criteria:\*\*\s+(.+?)(?=\*\*|\n\n|---)', step_body, re.DOTALL)
            if validation_match:
                criteria_content = validation_match.group(1).strip()
                validation_criteria = [line.strip('- ').strip() for line in criteria_content.split('\n') if line.strip().startswith('-')]
            
            # Extract warnings
            warnings = []
            warnings_match = re.search(r'\*\*Warnings:\*\*\s+(.+?)(?=\*\*|\n\n|---)', step_body, re.DOTALL)
            if warnings_match:
                warnings_content = warnings_match.group(1).strip()
                warnings = [line.strip('- ').strip() for line in warnings_content.split('\n') if line.strip().startswith('-')]
            
            # Extract estimated time
            estimated_time = None
            time_match = re.search(r'\*\*Estimated Time:\*\*\s+(.+?)(?=\n|$)', step_body)
            if time_match:
                estimated_time = time_match.group(1).strip()
            
            step = SOPStep(
                step_number=step_number,
                description=step_title,
                details=details,
                required=True,  # Default to required; could parse from MUST vs SHOULD
                validation_criteria=validation_criteria if validation_criteria else None,
                estimated_time=estimated_time,
                warnings=warnings if warnings else None
            )
            steps.append(step)
        
        if not steps:
            raise ValueError(f"No steps found in markdown SOP: {file_path}")
        
        # Extract keywords from title, description, and content
        keywords = []
        # Add words from title
        keywords.extend([word.lower() for word in re.findall(r'\b\w+\b', title) if len(word) > 3])
        # Add departments and roles as keywords
        keywords.extend([d.lower() for d in applicable_departments])
        keywords.extend([r.lower() for r in applicable_roles])
        # Deduplicate
        keywords = list(set(keywords))
        
        # Extract related SOPs
        related_sops = []
        related_match = re.search(r'##\s+Related SOPs\s+(.+?)(?=##|\Z)', content, re.DOTALL)
        if related_match:
            related_content = related_match.group(1).strip()
            related_lines = re.findall(r'-\s+.*?\(([^)]+)\)', related_content)
            related_sops = related_lines
        
        # Extract references
        references = []
        ref_match = re.search(r'##\s+References\s+(.+?)(?=##|\Z)', content, re.DOTALL)
        if ref_match:
            ref_content = ref_match.group(1).strip()
            ref_lines = [line.strip('- ').strip() for line in ref_content.split('\n') if line.strip().startswith('-')]
            references = ref_lines
        
        # Parse additional metadata
        author = metadata_dict.get('Author', 'Unknown')
        reviewer = metadata_dict.get('Reviewer', None)
        approval_status = metadata_dict.get('Approval Status', 'draft')
        review_frequency = metadata_dict.get('Review Frequency', None)
        
        # Extract from approval section if present
        approval_match = re.search(r'##\s+Approval\s+(.+?)(?=##|\Z)', content, re.DOTALL)
        if approval_match:
            approval_content = approval_match.group(1)
            author_match = re.search(r'\*\*Author:\*\*\s*(.+?)(?=\n|$)', approval_content)
            if author_match:
                author = author_match.group(1).strip()
            reviewer_match = re.search(r'\*\*Reviewer:\*\*\s*(.+?)(?=\n|$)', approval_content)
            if reviewer_match:
                reviewer = reviewer_match.group(1).strip()
            approval_match_status = re.search(r'\*\*Approval Status:\*\*\s*(.+?)(?=\n|$)', approval_content)
            if approval_match_status:
                approval_status = approval_match_status.group(1).strip().lower()
            review_freq_match = re.search(r'\*\*Review Frequency:\*\*\s*(.+?)(?=\n|$)', approval_content)
            if review_freq_match:
                review_frequency = review_freq_match.group(1).strip()
        
        # Create metadata object
        metadata = SOPMetadata(
            version=version,
            created_date=last_updated,  # Use last_updated as created_date if not specified
            last_updated=last_updated,
            author=author,
            reviewer=reviewer,
            approval_status=approval_status,
            review_frequency=review_frequency
        )
        
        # Create SOP object
        sop = SOP(
            id=sop_id,
            title=title,
            description=description,
            category=category,
            priority=priority,
            steps=steps,
            metadata=metadata,
            applicable_departments=applicable_departments,
            applicable_roles=applicable_roles,
            keywords=keywords,
            prerequisites=prerequisites if prerequisites else None,
            related_sops=related_sops if related_sops else None,
            references=references if references else None
        )
        
        return sop
    
    def _parse_sop_data(self, data: Dict) -> SOP:
        """
        Parse SOP data from dictionary with validation
        
        Args:
            data: Dictionary containing SOP data
            
        Returns:
            Validated SOP object
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Validate required fields
        required_fields = ['id', 'title', 'description', 'category', 'priority', 'steps', 'metadata']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
        
        # Parse steps
        steps = []
        for step_data in data.get('steps', []):
            step = SOPStep(
                step_number=step_data['step_number'],
                description=step_data['description'],
                details=step_data.get('details'),
                required=step_data.get('required', True),
                validation_criteria=step_data.get('validation_criteria'),
                estimated_time=step_data.get('estimated_time'),
                warnings=step_data.get('warnings')
            )
            steps.append(step)
        
        if not steps:
            raise ValueError(f"SOP must have at least one step")
        
        # Parse metadata
        metadata_data = data.get('metadata', {})
        metadata = SOPMetadata(
            version=metadata_data.get('version', '1.0'),
            created_date=metadata_data.get('created_date', ''),
            last_updated=metadata_data.get('last_updated', ''),
            author=metadata_data.get('author', ''),
            reviewer=metadata_data.get('reviewer'),
            approval_status=metadata_data.get('approval_status', 'draft'),
            review_frequency=metadata_data.get('review_frequency')
        )
        
        # Create SOP
        sop = SOP(
            id=data['id'],
            title=data['title'],
            description=data['description'],
            category=data['category'],
            priority=data['priority'],
            steps=steps,
            metadata=metadata,
            applicable_departments=data.get('applicable_departments', []),
            applicable_roles=data.get('applicable_roles', []),
            keywords=data.get('keywords', []),
            prerequisites=data.get('prerequisites'),
            related_sops=data.get('related_sops'),
            references=data.get('references')
        )
        
        return sop
    
    def load_sop_from_dict(self, data: Dict, repository_name: str = "dynamic") -> SOP:
        """
        Load a single SOP from a dictionary (useful for MCP integration)
        
        Args:
            data: SOP data as dictionary
            repository_name: Repository to add the SOP to
            
        Returns:
            Loaded SOP object
        """
        sop = self._parse_sop_data(data)
        
        # Add to repository or create new one
        if repository_name not in self.repositories:
            self.repositories[repository_name] = SOPRepository(
                name=repository_name,
                description="Dynamically loaded SOPs",
                source_type="dynamic"
            )
        
        self.repositories[repository_name].add_sop(sop)
        return sop
    
    def get_repository(self, name: str) -> Optional[SOPRepository]:
        """Get a repository by name"""
        return self.repositories.get(name)
    
    def get_all_sops(self) -> List[SOP]:
        """Get all SOPs from all repositories"""
        all_sops = []
        for repo in self.repositories.values():
            all_sops.extend(repo.sops)
        return all_sops
    
    def get_sop_by_id(self, sop_id: str) -> Optional[SOP]:
        """Search for an SOP by ID across all repositories"""
        for repo in self.repositories.values():
            sop = repo.get_sop_by_id(sop_id)
            if sop:
                return sop
        return None
    
    def get_repository_summary(self) -> str:
        """Get a summary of all loaded repositories"""
        if not self.repositories:
            return "No SOP repositories loaded."
        
        lines = ["📚 Loaded SOP Repositories:\n"]
        for name, repo in self.repositories.items():
            lines.append(f"  • {name}: {len(repo.sops)} SOPs")
            categories = repo.get_all_categories()
            if categories:
                lines.append(f"    Categories: {', '.join(categories)}")
        
        return "\n".join(lines)
