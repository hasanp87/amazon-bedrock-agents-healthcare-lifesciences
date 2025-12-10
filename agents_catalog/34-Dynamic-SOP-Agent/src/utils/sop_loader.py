"""
SOP loading utilities
"""

import json
import yaml
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from ..models.sop_models import SOP, SOPStep, SOPMetadata, SOPRepository


class SOPLoader:
    """Utility class for loading SOPs from various sources"""
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize the SOP loader
        
        Args:
            base_path: Base directory path for local SOP files
        """
        self.base_path = base_path or "examples/sops"
    
    def load_from_json(self, file_path: str) -> SOP:
        """
        Load an SOP from a JSON file
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            SOP object
        """
        with open(file_path, 'r') as f:
            data = json.load(f)
        return self._dict_to_sop(data)
    
    def load_from_yaml(self, file_path: str) -> SOP:
        """
        Load an SOP from a YAML file
        
        Args:
            file_path: Path to the YAML file
            
        Returns:
            SOP object
        """
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        return self._dict_to_sop(data)
    
    def load_directory(self, directory: str) -> SOPRepository:
        """
        Load all SOPs from a directory
        
        Args:
            directory: Directory containing SOP files
            
        Returns:
            SOPRepository containing all loaded SOPs
        """
        repository = SOPRepository(
            name=os.path.basename(directory),
            description=f"SOPs loaded from {directory}",
            source_type="local",
            source_url=directory
        )
        
        path = Path(directory)
        if not path.exists():
            return repository
        
        # Load JSON files
        for json_file in path.glob("*.json"):
            try:
                sop = self.load_from_json(str(json_file))
                repository.add_sop(sop)
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
        
        # Load YAML files
        for yaml_file in path.glob("*.yaml"):
            try:
                sop = self.load_from_yaml(str(yaml_file))
                repository.add_sop(sop)
            except Exception as e:
                print(f"Error loading {yaml_file}: {e}")
        
        for yml_file in path.glob("*.yml"):
            try:
                sop = self.load_from_yaml(str(yml_file))
                repository.add_sop(sop)
            except Exception as e:
                print(f"Error loading {yml_file}: {e}")
        
        return repository
    
    def _dict_to_sop(self, data: Dict[str, Any]) -> SOP:
        """Convert dictionary to SOP object"""
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
        
        # Create SOP object
        sop = SOP(
            id=data['id'],
            title=data['title'],
            description=data['description'],
            category=data.get('category', 'general'),
            priority=data.get('priority', 'medium'),
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
    
    def save_to_json(self, sop: SOP, file_path: str) -> None:
        """
        Save an SOP to a JSON file
        
        Args:
            sop: SOP object to save
            file_path: Path where to save the JSON file
        """
        with open(file_path, 'w') as f:
            json.dump(sop.to_dict(), f, indent=2)
    
    def save_to_yaml(self, sop: SOP, file_path: str) -> None:
        """
        Save an SOP to a YAML file
        
        Args:
            sop: SOP object to save
            file_path: Path where to save the YAML file
        """
        with open(file_path, 'w') as f:
            yaml.dump(sop.to_dict(), f, default_flow_style=False)
