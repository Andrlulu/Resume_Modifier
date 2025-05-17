import re
import random
import string
from app.models.temp import UserSite
from app.extensions import db

def sanitize_username(username):
    """Convert username to a valid subdomain."""
    # Remove special characters, keep only alphanumeric and hyphens
    sanitized = re.sub(r'[^a-zA-Z0-9-]', '', username.lower().replace(' ', '-'))
    # Ensure it starts with a letter or number
    if not sanitized or not sanitized[0].isalnum():
        sanitized = 'user-' + sanitized
    # Truncate if too long
    return sanitized[:50]  # Safe subdomain length

def generate_unique_subdomain(user_id, username):
    """Generate a unique subdomain for a user."""
    base_subdomain = sanitize_username(username)
    
    # Check if base subdomain is available
    subdomain = base_subdomain
    existing = UserSite.query.filter_by(subdomain=subdomain).first()
    
    # If not available, add random suffix
    if existing:
        # Try up to 5 times with numbers
        for i in range(1, 6):
            subdomain = f"{base_subdomain}{i}"
            if not UserSite.query.filter_by(subdomain=subdomain).first():
                return subdomain
        
        # If still not unique, add random string
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        subdomain = f"{base_subdomain}-{random_suffix}"
    
    return subdomain

def get_site_url(subdomain):
    """Get the full URL for a user's site."""
    return f"https://{subdomain}.resume.mintmelon.ca"

def is_valid_subdomain(subdomain):
    """Validate if a subdomain meets requirements."""
    # Check length
    if len(subdomain) < 3 or len(subdomain) > 63:
        return False
    
    # Check pattern (start/end with alphanumeric, hyphens in middle)
    if not re.match(r'^[a-z0-9]([a-z0-9-]{1,61}[a-z0-9])?$', subdomain):
        return False
    
    # Check for reserved names
    reserved_names = ['www', 'mail', 'admin', 'api', 'app', 'staging']
    if subdomain in reserved_names:
        return False
    
    return True 