from notion_client import Client
from typing import Dict, List, Any, Optional, Union


class NotionConnection:
    """
    A simplified class to handle CRUD operations with Notion databases.
    Uses the official notion-client library for API interactions.
    """
    
    def __init__(self, token: str):
        """
        Initialize the NotionConnection with your Integration Token.
        
        Args:
            token (str): Your Notion Integration Secret Token
        """
        self.client = Client(auth=token)
    
    def get_all_rows(self, database_id: str, filter_params: Optional[Dict] = None, 
                     sorts: Optional[List[Dict]] = None) -> List[Dict]:
        """
        Get all rows from a database, handling pagination automatically.
        
        Args:
            database_id (str): The ID of the database
            filter_params (Dict, optional): Filter criteria
            sorts (List[Dict], optional): Sort criteria
            
        Returns:
            List[Dict]: All matching rows
        """
        all_results = []
        query_params = {
            "database_id": database_id
        }
        
        if filter_params:
            query_params["filter"] = filter_params
        
        if sorts:
            query_params["sorts"] = sorts
        
        # Initial query
        response = self.client.databases.query(**query_params)
        all_results.extend(response.get("results", []))
        
        # Handle pagination
        while response.get("has_more", False):
            query_params["start_cursor"] = response.get("next_cursor")
            response = self.client.databases.query(**query_params)
            all_results.extend(response.get("results", []))
        
        return all_results
    
    def get_row(self, page_id: str) -> Dict:
        """
        Get a single row by its page ID.
        
        Args:
            page_id (str): The ID of the page/row
            
        Returns:
            Dict: Row details
        """
        return self.client.pages.retrieve(page_id=page_id)
    
    def add_row(self, database_id: str, properties: Dict) -> Dict:
        """
        Add a new row to a database.
        
        Args:
            database_id (str): The database to add the row to
            properties (Dict): The row properties (must match the database schema)
            
        Returns:
            Dict: The created row
        """
        return self.client.pages.create(
            parent={"database_id": database_id},
            properties=properties
        )
    
    def update_row(self, page_id: str, properties: Dict) -> Dict:
        """
        Update a row's properties.
        
        Args:
            page_id (str): The ID of the row to update
            properties (Dict): Updated properties
            
        Returns:
            Dict: The updated row
        """
        return self.client.pages.update(
            page_id=page_id, 
            properties=properties
        )
    
    # Helper methods for creating property values
    
    @staticmethod
    def text_property(content: str) -> Dict:
        """Helper for creating text property values"""
        return {
            "rich_text": [
                {
                    "type": "text", 
                    "text": {"content": content}
                }
            ]
        }
    
    @staticmethod
    def title_property(content: str) -> Dict:
        """Helper for creating title property values"""
        return {
            "title": [
                {
                    "type": "text", 
                    "text": {"content": content}
                }
            ]
        }
    
    @staticmethod
    def number_property(number: Union[int, float]) -> Dict:
        """Helper for creating number property values"""
        return {"number": number}
    
    @staticmethod
    def select_property(option: str) -> Dict:
        """Helper for creating select property values"""
        return {"select": {"name": option}}
    
    @staticmethod
    def multi_select_property(options: List[str]) -> Dict:
        """Helper for creating multi-select property values"""
        return {"multi_select": [{"name": option} for option in options]}
    
    @staticmethod
    def date_property(start: str, end: Optional[str] = None) -> Dict:
        """
        Helper for creating date property values.
        Dates should be in ISO 8601 format, e.g., "2023-04-01" or "2023-04-01T12:00:00Z"
        """
        date_obj = {"start": start}
        if end:
            date_obj["end"] = end
        return {"date": date_obj}
    
    @staticmethod
    def checkbox_property(checked: bool) -> Dict:
        """Helper for creating checkbox property values"""
        return {"checkbox": checked}
    
    @staticmethod
    def url_property(url: str) -> Dict:
        """Helper for creating URL property values"""
        return {"url": url}
    
    @staticmethod
    def email_property(email: str) -> Dict:
        """Helper for creating email property values"""
        return {"email": email}
    
    @staticmethod
    def phone_property(phone: str) -> Dict:
        """Helper for creating phone number property values"""
        return {"phone_number": phone}
    
    @staticmethod
    def relation_property(page_ids: List[str]) -> Dict:
        """Helper for creating relation property values"""
        return {"relation": [{"id": page_id} for page_id in page_ids]}