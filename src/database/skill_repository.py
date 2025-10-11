from typing import Optional, Dict, Any, List
from supabase import Client
from .supabase_client import get_supabase_client
import json

class SkillRepository:
    """
    Handles all database operations for skills and job roles
    """

    def __init__(self, client: Optional[Client] = None):
        self.client = client or get_supabase_client()

    def get_all_job_roles(self) -> Dict[str, List[str]]:
        """
        Get all job roles with their required skills
        Returns a dict mapping role names to skill lists
        """
        try:
            response = self.client.table("job_roles").select("*").execute()

            if response.data:
                roles_map = {}
                for role in response.data:
                    role_name = role.get("role_name")
                    required_skills = role.get("required_skills", [])

                    if isinstance(required_skills, str):
                        required_skills = json.loads(required_skills)

                    roles_map[role_name] = required_skills

                return roles_map
            return {}

        except Exception as e:
            print(f"Error fetching job roles: {e}")
            return {}

    def get_job_role_details(self, role_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific job role
        """
        try:
            response = self.client.table("job_roles").select("*").eq(
                "role_name", role_name
            ).maybeSingle().execute()

            if response.data:
                role = response.data
                if isinstance(role.get("required_skills"), str):
                    role["required_skills"] = json.loads(role["required_skills"])
                return role
            return None

        except Exception as e:
            print(f"Error fetching role details: {e}")
            return None

    def get_roles_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all job roles in a specific category
        """
        try:
            response = self.client.table("job_roles").select("*").eq(
                "category", category
            ).execute()

            if response.data:
                for role in response.data:
                    if isinstance(role.get("required_skills"), str):
                        role["required_skills"] = json.loads(role["required_skills"])
                return response.data
            return []

        except Exception as e:
            print(f"Error fetching roles by category: {e}")
            return []

    def get_roles_by_experience(self, experience_level: str) -> List[Dict[str, Any]]:
        """
        Get all job roles for a specific experience level
        """
        try:
            response = self.client.table("job_roles").select("*").eq(
                "experience_level", experience_level
            ).execute()

            if response.data:
                for role in response.data:
                    if isinstance(role.get("required_skills"), str):
                        role["required_skills"] = json.loads(role["required_skills"])
                return response.data
            return []

        except Exception as e:
            print(f"Error fetching roles by experience: {e}")
            return []

    def get_all_skills(self) -> List[Dict[str, Any]]:
        """
        Get all skills from the skills database
        """
        try:
            response = self.client.table("skills_database").select("*").order(
                "popularity_score", desc=True
            ).execute()

            if response.data:
                for skill in response.data:
                    if isinstance(skill.get("synonyms"), str):
                        skill["synonyms"] = json.loads(skill["synonyms"])
                return response.data
            return []

        except Exception as e:
            print(f"Error fetching skills: {e}")
            return []

    def get_skills_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all skills in a specific category
        """
        try:
            response = self.client.table("skills_database").select("*").eq(
                "category", category
            ).order("popularity_score", desc=True).execute()

            if response.data:
                for skill in response.data:
                    if isinstance(skill.get("synonyms"), str):
                        skill["synonyms"] = json.loads(skill["synonyms"])
                return response.data
            return []

        except Exception as e:
            print(f"Error fetching skills by category: {e}")
            return []

    def search_skills(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for skills by name
        """
        try:
            response = self.client.table("skills_database").select("*").ilike(
                "skill_name", f"%{query}%"
            ).execute()

            if response.data:
                for skill in response.data:
                    if isinstance(skill.get("synonyms"), str):
                        skill["synonyms"] = json.loads(skill["synonyms"])
                return response.data
            return []

        except Exception as e:
            print(f"Error searching skills: {e}")
            return []

    def get_skill_categories(self) -> List[str]:
        """
        Get all unique skill categories
        """
        try:
            response = self.client.table("skills_database").select("category").execute()

            if response.data:
                categories = list(set(item["category"] for item in response.data))
                return sorted(categories)
            return []

        except Exception as e:
            print(f"Error fetching categories: {e}")
            return []

    def get_role_categories(self) -> List[str]:
        """
        Get all unique job role categories
        """
        try:
            response = self.client.table("job_roles").select("category").execute()

            if response.data:
                categories = list(set(item["category"] for item in response.data))
                return sorted(categories)
            return []

        except Exception as e:
            print(f"Error fetching role categories: {e}")
            return []

    def add_custom_skill(
        self,
        skill_name: str,
        category: str,
        synonyms: List[str] = None,
        popularity_score: int = 50
    ) -> Optional[Dict[str, Any]]:
        """
        Add a new skill to the database
        """
        try:
            skill_data = {
                "skill_name": skill_name,
                "category": category,
                "synonyms": json.dumps(synonyms or []),
                "popularity_score": popularity_score
            }

            response = self.client.table("skills_database").insert(skill_data).execute()

            if response.data:
                return response.data[0]
            return None

        except Exception as e:
            print(f"Error adding skill: {e}")
            return None
