from typing import Optional, Dict, Any
from supabase import Client
from .supabase_client import get_supabase_client

class AuthService:
    """
    Handles user authentication and profile management
    """

    def __init__(self, client: Optional[Client] = None):
        self.client = client or get_supabase_client()

    def sign_up(self, email: str, password: str, full_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Register a new user
        """
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password
            })

            if response.user:
                user_data = {
                    "id": response.user.id,
                    "email": email,
                    "full_name": full_name or email.split('@')[0]
                }
                self.client.table("users").insert(user_data).execute()

                return {
                    "success": True,
                    "user": response.user,
                    "message": "Account created successfully!"
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to create account"
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }

    def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """
        Sign in an existing user
        """
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if response.user:
                self.client.table("users").update({
                    "last_login": "now()"
                }).eq("id", response.user.id).execute()

                return {
                    "success": True,
                    "user": response.user,
                    "session": response.session,
                    "message": "Signed in successfully!"
                }
            else:
                return {
                    "success": False,
                    "message": "Invalid credentials"
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }

    def sign_out(self) -> Dict[str, Any]:
        """
        Sign out current user
        """
        try:
            self.client.auth.sign_out()
            return {
                "success": True,
                "message": "Signed out successfully!"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }

    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Get currently authenticated user
        """
        try:
            user = self.client.auth.get_user()
            if user:
                return user.user
            return None
        except:
            return None

    def get_session(self) -> Optional[Any]:
        """
        Get current session
        """
        try:
            session = self.client.auth.get_session()
            return session
        except:
            return None
