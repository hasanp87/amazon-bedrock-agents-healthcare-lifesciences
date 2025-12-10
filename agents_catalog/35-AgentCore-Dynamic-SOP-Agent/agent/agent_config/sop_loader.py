"""
SOP Loader for loading SOPs from various sources
"""

import json
import yaml
import os
from pathlib import Path
from typing import List, Dict, Optional
from .sop_models import SOP, SOPStep, SOPMetadata, SOPRepository


class SOPLoader:
    """Loads SOPs from various sources"""
    
    def __init__(self):
        self.repositories: Dict[str, SOPRepository] = {}
    
    def load_from_directory(self, directory_path: str, repository_name: str = "local") -> SOPRepository:
        """
        Load all SOPs from a directory (JSON and YAML files)
        
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
        
        # Load JSON files
        for json_file in path.glob("*.json"):
            try:
                sop = self._load_sop_from_json(json_file)
                repository.add_sop(sop)
                print(f"✓ Loaded SOP: {sop.id} from {json_file.name}")
            except Exception as e:
                print(f"✗ Error loading {json_file.name}: {e}")
        
        # Load YAML files
        for yaml_file in path.glob("*.yaml"):
            try:
                sop = self._load_sop_from_yaml(yaml_file)
                repository.add_sop(sop)
                print(f"✓ Loaded SOP: {sop.id} from {yaml_file.name}")
            except Exception as e:
                print(f"✗ Error loading {yaml_file.name}: {e}")
        
        for yml_file in path.glob("*.yml"):
            try:
                sop = self._load_sop_from_yaml(yml_file)
                repository.add_sop(sop)
                print(f"✓ Loaded SOP: {sop.id} from {yml_file.name}")
            except Exception as e:
                print(f"✗ Error loading {yml_file.name}: {e}")
        
        self.repositories[repository_name] = repository
        return repository
    
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
    
    def _parse_sop_data(self, data: Dict) -> SOP:
        """Parse SOP data from dictionary"""
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
