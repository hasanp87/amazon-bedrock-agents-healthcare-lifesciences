"""
MCP (Model Context Protocol) connector for accessing external SOP repositories
"""

from typing import List, Dict, Optional, Any
from ..models.sop_models import SOPRepository, SOP
from .sop_loader import SOPLoader


class MCPConnector:
    """
    Connector for integrating with MCP servers to access external SOP repositories
    
    This class provides a framework for connecting to MCP servers such as:
    - Git Repo Research MCP Server for accessing SOPs in git repositories
    - AWS Documentation MCP Server for accessing AWS-related SOPs
    - Custom MCP servers for organization-specific SOP repositories
    """
    
    def __init__(self):
        """Initialize the MCP connector"""
        self.repositories: Dict[str, SOPRepository] = {}
        self.sop_loader = SOPLoader()
    
    def register_repository(self, name: str, config: Dict[str, Any]) -> SOPRepository:
        """
        Register an external SOP repository
        
        Args:
            name: Unique name for the repository
            config: Configuration dictionary containing:
                - source_type: Type of source ('mcp', 'git', 'api', etc.)
                - source_url: URL or path to the repository
                - description: Description of the repository
                
        Returns:
            SOPRepository object
        """
        repository = SOPRepository(
            name=name,
            description=config.get('description', f'{name} repository'),
            source_type=config.get('source_type', 'mcp'),
            source_url=config.get('source_url')
        )
        
        self.repositories[name] = repository
        return repository
    
    def connect_git_repo_mcp(self, repo_name: str, repo_url: str, sop_path: str = 'sops') -> SOPRepository:
        """
        Connect to a git repository via Git Repo Research MCP Server
        
        Args:
            repo_name: Name for this repository
            repo_url: Git repository URL
            sop_path: Path within the repository where SOPs are stored
            
        Returns:
            SOPRepository object
        """
        config = {
            'source_type': 'mcp_git',
            'source_url': repo_url,
            'description': f'SOPs from Git repository: {repo_url}',
            'sop_path': sop_path
        }
        
        repository = self.register_repository(repo_name, config)
        
        # In a real implementation, this would use the MCP server to fetch SOPs
        # For now, we simulate the connection
        print(f"📡 Connected to Git repository via MCP: {repo_url}")
        print(f"   SOP path: {sop_path}")
        
        return repository
    
    def connect_aws_docs_mcp(self, service_names: List[str]) -> SOPRepository:
        """
        Connect to AWS Documentation via AWS Documentation MCP Server
        
        Args:
            service_names: List of AWS service names to retrieve SOPs for
            
        Returns:
            SOPRepository object
        """
        config = {
            'source_type': 'mcp_aws_docs',
            'source_url': 'https://docs.aws.amazon.com',
            'description': f'AWS service SOPs for: {", ".join(service_names)}',
            'services': service_names
        }
        
        repository = self.register_repository('aws_documentation', config)
        
        print(f"📡 Connected to AWS Documentation via MCP")
        print(f"   Services: {', '.join(service_names)}")
        
        return repository
    
    def connect_custom_mcp(self, name: str, mcp_config: Dict[str, Any]) -> SOPRepository:
        """
        Connect to a custom MCP server
        
        Args:
            name: Name for this repository
            mcp_config: Configuration for the custom MCP server
            
        Returns:
            SOPRepository object
        """
        config = {
            'source_type': 'mcp_custom',
            'description': mcp_config.get('description', f'Custom MCP: {name}'),
            **mcp_config
        }
        
        repository = self.register_repository(name, config)
        
        print(f"📡 Connected to custom MCP server: {name}")
        
        return repository
    
    def load_sops_from_repository(self, repo_name: str, local_cache_path: Optional[str] = None) -> List[SOP]:
        """
        Load SOPs from a registered repository
        
        Args:
            repo_name: Name of the registered repository
            local_cache_path: Optional local path where SOPs might be cached
            
        Returns:
            List of SOP objects
        """
        if repo_name not in self.repositories:
            raise ValueError(f"Repository '{repo_name}' not registered")
        
        repository = self.repositories[repo_name]
        
        # If local cache path is provided, try loading from there
        if local_cache_path:
            try:
                cached_repo = self.sop_loader.load_directory(local_cache_path)
                repository.sops = cached_repo.sops
                print(f"✅ Loaded {len(repository.sops)} SOPs from local cache")
                return repository.sops
            except Exception as e:
                print(f"⚠️  Could not load from local cache: {e}")
        
        # In a real implementation, this would fetch from the MCP server
        print(f"📥 Would fetch SOPs from MCP server for: {repo_name}")
        print(f"   Source type: {repository.source_type}")
        print(f"   Source URL: {repository.source_url}")
        
        return repository.sops
    
    def sync_repository(self, repo_name: str) -> int:
        """
        Sync a repository to fetch latest SOPs
        
        Args:
            repo_name: Name of the repository to sync
            
        Returns:
            Number of SOPs synced
        """
        if repo_name not in self.repositories:
            raise ValueError(f"Repository '{repo_name}' not registered")
        
        # In a real implementation, this would trigger a sync via MCP
        print(f"🔄 Syncing repository: {repo_name}")
        
        return len(self.repositories[repo_name].sops)
    
    def get_repository(self, repo_name: str) -> Optional[SOPRepository]:
        """
        Get a registered repository by name
        
        Args:
            repo_name: Name of the repository
            
        Returns:
            SOPRepository object or None if not found
        """
        return self.repositories.get(repo_name)
    
    def list_repositories(self) -> List[str]:
        """
        List all registered repositories
        
        Returns:
            List of repository names
        """
        return list(self.repositories.keys())
    
    def get_all_sops(self) -> List[SOP]:
        """
        Get all SOPs from all registered repositories
        
        Returns:
            List of all SOP objects
        """
        all_sops = []
        for repository in self.repositories.values():
            all_sops.extend(repository.sops)
        return all_sops
    
    def search_sops(self, keyword: str) -> List[SOP]:
        """
        Search for SOPs across all repositories by keyword
        
        Args:
            keyword: Keyword to search for
            
        Returns:
            List of matching SOP objects
        """
        matching_sops = []
        keyword_lower = keyword.lower()
        
        for repository in self.repositories.values():
            for sop in repository.sops:
                # Check title, description, and keywords
                if (keyword_lower in sop.title.lower() or
                    keyword_lower in sop.description.lower() or
                    keyword_lower in [k.lower() for k in sop.keywords]):
                    matching_sops.append(sop)
        
        return matching_sops
