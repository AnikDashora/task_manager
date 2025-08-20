class User:
    def __init__(self):
        self.user_id = None
        self.name = None
        self.email = None
        self.password = None #hash password
        self.theme = "Light"
        self.user_exist = False

    def set_user_data(self, user_id=None, name=None, email=None, password=None,theme = "Light"):
        """
        Set user data for the User instance
        
        Args:
            user_id (int, optional): User ID
            name (str, optional): User name
            email (str, optional): User email
            password (str, optional): User password
        """
        if user_id is not None:
            self.user_id = user_id
        if name is not None:
            self.name = name
        if email is not None:
            self.email = email
        if password is not None:
            self.password = password
        self.theme = "Light"

    def set_user_exist(self):
        if(self.user_id is not None):
            self.user_exist = True