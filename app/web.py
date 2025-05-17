from flask import Blueprint, request, jsonify, render_template_string, Response
from app.extensions import db
from app.utils.jwt_utils import token_required
from app.models.temp import Resume
from app.models.temp import UserSite
from app.utils.subdomain_utils import generate_unique_subdomain, get_site_url
import html
import bleach
from functools import wraps
import time
from datetime import datetime
import re
import traceback

# Dictionary to store API request counts
request_counter = {}
RATE_LIMIT = 10  # Maximum requests per minute
RATE_WINDOW = 60  # Time window in seconds

def rate_limit(f):
    """Rate limiting decorator for API endpoints."""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Get user IP or ID for rate limiting
        identifier = request.user.get('user_id', request.remote_addr)
        
        # Get current timestamp
        now = time.time()
        
        # Initialize or get current request info
        if identifier not in request_counter:
            request_counter[identifier] = {'count': 0, 'reset_time': now + RATE_WINDOW}
        
        # Check if we need to reset the counter
        if now > request_counter[identifier]['reset_time']:
            request_counter[identifier] = {'count': 0, 'reset_time': now + RATE_WINDOW}
        
        # Check if rate limit exceeded
        if request_counter[identifier]['count'] >= RATE_LIMIT:
            return jsonify({
                "error": "Rate limit exceeded. Try again later.",
                "retry_after": int(request_counter[identifier]['reset_time'] - now)
            }), 429
        
        # Increment request counter
        request_counter[identifier]['count'] += 1
        
        return f(*args, **kwargs)
    return decorated

web = Blueprint('web', __name__)

def sanitize_input(data):
    """Sanitize user input to prevent injection attacks."""
    if isinstance(data, dict):
        return {k: sanitize_input(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(i) for i in data]
    elif isinstance(data, str):
        # Basic XSS protection - remove script tags and dangerous attributes
        return bleach.clean(data, strip=True)
    else:
        return data

def validate_serial_number(serial):
    """Validate resume serial format."""
    if not serial:
        return False
    # Adjust pattern based on your actual serial format
    try:
        # Check if it's a valid integer
        serial_int = int(serial)
        return True
    except ValueError:
        return False

@web.route('/web/generate_personal_site/<serial_number>', methods=['GET'])
@token_required
@rate_limit
def generate_personal_site(serial_number):
    """Generate a personal website based on the user's resume.
    
    Uses the resume serial from the URL path parameter and user_id from the token.
    Creates a unique subdomain for the user and stores the HTML.
    Returns both the HTML and the subdomain URL.
    """
    try:
        # Extract user_id from the JWT payload that was added to request by token_required
        user_id = request.user.get('user_id')
        
        if not user_id:
            return jsonify({"error": "User ID not found in token"}), 401
        
        # Validate resume serial format
        if not validate_serial_number(serial_number):
            return jsonify({"error": "Invalid resume serial format"}), 400
        
        # Convert to integer for database query
        serial_number_int = int(serial_number)
        
        # Fetch the user's resume using the serial_number
        resume = Resume.query.filter_by(user_id=user_id, serial_number=serial_number_int).first()
        
        if not resume:
            return jsonify({"error": "Resume not found"}), 404
        
        # Use the parsed resume data to generate the website
        parsed_resume = resume.parsed_resume
        
        if not parsed_resume:
            return jsonify({"error": "No parsed resume data available"}), 404
        
        # Sanitize all resume data to prevent XSS
        sanitized_resume = sanitize_input(parsed_resume)
        
        # Add current date to template context
        sanitized_resume['generation_date'] = datetime.now().strftime("%B %d, %Y")
        
        # HTML template using Jinja2 syntax with updated field mappings
        html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{{ userInfo.firstName }} {{ userInfo.lastName }}</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f8f9fa;
                }
                header {
                    background-color: #343a40;
                    color: white;
                    padding: 2rem;
                    text-align: center;
                    border-radius: 5px;
                    margin-bottom: 2rem;
                }
                h1 {
                    margin-bottom: 0.5rem;
                    font-size: 2.5rem;
                }
                h3 {
                    font-weight: normal;
                    margin-top: 0.5rem;
                    font-style: italic;
                }
                .contact-info {
                    margin-top: 1rem;
                    font-size: 1.1rem;
                }
                section {
                    background-color: white;
                    padding: 2rem;
                    margin-bottom: 2rem;
                    border-radius: 5px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }
                h2 {
                    border-bottom: 2px solid #007bff;
                    padding-bottom: 0.5rem;
                    margin-bottom: 1.5rem;
                    color: #007bff;
                }
                .experience-item, .education-item, .project-item, .skill-item {
                    margin-bottom: 1.5rem;
                }
                .company-name, .school-name, .project-title {
                    font-weight: bold;
                    font-size: 1.2rem;
                }
                .job-title, .degree, .project-role {
                    font-weight: bold;
                    color: #343a40;
                }
                .date {
                    color: #6c757d;
                    font-style: italic;
                }
                .skill-list {
                    display: flex;
                    flex-direction: column;
                    gap: 10px;
                }
                .skill-item {
                    background-color: #e9ecef;
                    padding: 10px 15px;
                    border-radius: 5px;
                    font-size: 1rem;
                }
                footer {
                    text-align: center;
                    padding: 1rem;
                    color: #6c757d;
                    font-size: 0.9rem;
                }
                @media (max-width: 768px) {
                    body {
                        padding: 10px;
                    }
                    header, section {
                        padding: 1.5rem;
                    }
                }
            </style>
        </head>
        <body>
            <header>
                <h1>{{ userInfo.firstName }} {{ userInfo.lastName }}</h1>
                {% if userInfo.headLine %}<h3>{{ userInfo.headLine }}</h3>{% endif %}
                <div class="contact-info">
                    {% if userInfo.email %}{{ userInfo.email }}{% endif %}
                    {% if userInfo.phoneNumber %} | {{ userInfo.phoneNumber }}{% endif %}
                    {% if userInfo.websiteOrOtherProfileURL %} | <a href="{{ userInfo.websiteOrOtherProfileURL }}" style="color: white;">Portfolio</a>{% endif %}
                    {% if userInfo.linkedInURL %} | <a href="{{ userInfo.linkedInURL }}" style="color: white;">LinkedIn</a>{% endif %}
                </div>
            </header>
            
            {% if summary %}
            <section>
                <h2>About Me</h2>
                <p>{{ summary }}</p>
            </section>
            {% endif %}
            
            {% if workExperience and workExperience|length > 0 %}
            <section>
                <h2>Professional Experience</h2>
                {% for job in workExperience %}
                <div class="experience-item">
                    <div class="company-name">{{ job.company }}</div>
                    <div class="job-title">{{ job.title }}</div>
                    <div class="date">
                        {{ job.fromDate }} - {% if job.isPresent %}Present{% else %}{{ job.toDate }}{% endif %}
                        {% if job.city or job.country %} | {{ job.city }}{% if job.city and job.country %}, {% endif %}{{ job.country }}{% endif %}
                    </div>
                    {% if job.description %}
                    <p>{{ job.description }}</p>
                    {% endif %}
                </div>
                {% endfor %}
            </section>
            {% endif %}
            
            {% if project and project|length > 0 %}
            <section>
                <h2>Projects</h2>
                {% for proj in project %}
                <div class="project-item">
                    <div class="project-title">{{ proj.title }}</div>
                    <div class="project-role">{{ proj.projectRole }}</div>
                    <div class="date">
                        {{ proj.fromDate }} - {% if proj.isPresent %}Present{% else %}{{ proj.toDate }}{% endif %}
                    </div>
                    {% if proj.description %}
                    <p>{{ proj.description }}</p>
                    {% endif %}
                </div>
                {% endfor %}
            </section>
            {% endif %}
            
            {% if education and education|length > 0 %}
            <section>
                <h2>Education</h2>
                {% for edu in education %}
                <div class="education-item">
                    <div class="school-name">{{ edu.institutionName }}</div>
                    <div class="degree">{{ edu.degree }} {% if edu.fieldOfStudy %}in {{ edu.fieldOfStudy }}{% endif %}</div>
                    <div class="date">
                        {% if edu.fromDate %}{{ edu.fromDate }} - {% endif %}
                        {% if edu.isPresent %}Present{% else %}{{ edu.toDate }}{% endif %}
                        {% if edu.city or edu.country %} | {{ edu.city }}{% if edu.city and edu.country %}, {% endif %}{{ edu.country }}{% endif %}
                    </div>
                    {% if edu.description %}
                    <p>{{ edu.description }}</p>
                    {% endif %}
                </div>
                {% endfor %}
            </section>
            {% endif %}
            
            {% if skills and skills|length > 0 %}
            <section>
                <h2>Skills</h2>
                <div class="skill-list">
                    {% for skill in skills %}
                    <div class="skill-item">{{ skill }}</div>
                    {% endfor %}
                </div>
            </section>
            {% endif %}
            
            {% if certifications and certifications|length > 0 %}
            <section>
                <h2>Certifications</h2>
                <ul>
                    {% for cert in certifications %}
                    <li>{{ cert.name }} {% if cert.issuer %}({{ cert.issuer }}){% endif %}</li>
                    {% endfor %}
                </ul>
            </section>
            {% endif %}
            
            <footer>
                <p>Generated on {{ generation_date }}</p>
            </footer>
        </body>
        </html>
        """
        
        # Add current date to template context
        sanitized_resume['generation_date'] = datetime.now().strftime("%B %d, %Y")

        
        
        # Render the template using render_template_string
        rendered_html = render_template_string(html_template, **sanitized_resume)
        
        # Return the HTML directly to be rendered in the browser
        # return Response(rendered_html, mimetype='text/html')
        # test
        # return jsonify({
        #     "status": 200,
        #     "html": rendered_html,
        # }), 200
        
        
        

        # Generate a unique subdomain based on user's name
        username = f"{sanitized_resume.get('userInfo', {}).get('firstName', '')} {sanitized_resume.get('userInfo', {}).get('lastName', '')}"
        if not username.strip():
            username = f"user{user_id}"
        
        # Check if a site already exists for this user and resume
        existing_site = UserSite.query.filter_by(user_id=user_id, resume_serial=serial_number_int).first()
        
        if existing_site:
            # Update existing site
            existing_site.html_content = rendered_html
            existing_site.updated_at = datetime.utcnow()
            subdomain = existing_site.subdomain
        else:
            # Create new subdomain and site
            subdomain = generate_unique_subdomain(user_id, username)
            new_site = UserSite(
                user_id=user_id,
                resume_serial=serial_number_int,
                subdomain=subdomain,
                html_content=rendered_html
            )
            db.session.add(new_site)
        
        # Commit changes to database
        db.session.commit()
        
        # Generate the full URL
        site_url = get_site_url(subdomain)
        
        # Return both the HTML and the subdomain URL
        return jsonify({
            "status": 200,
            "html": rendered_html,
            "site_url": site_url,
            "subdomain": subdomain
        }), 200
        
    except Exception as e:
        # Log the error for debugging
        error_traceback = traceback.format_exc()
        print(f"Error generating personal site: {str(e)}")
        print(error_traceback)
        
        # Return a generic error message to avoid exposing sensitive information
        return jsonify({
            "error": "An error occurred while generating the personal site. Please try again later."
        }), 500

@web.route('/web/serve_site/<subdomain>', methods=['GET'])
def serve_site(subdomain):
    """Serve a user's website by subdomain.
    
    This route is used by the reverse proxy to serve user sites.
    """
    try:
        # Sanitize the subdomain input
        if not re.match(r'^[a-zA-Z0-9-]+$', subdomain):
            return jsonify({"error": "Invalid subdomain format"}), 400
            
        # Fetch the user's site
        site = UserSite.query.filter_by(subdomain=subdomain.lower()).first()
        
        if not site:
            return jsonify({"error": "Site not found"}), 404
            
        # Return the HTML content
        return Response(site.html_content, mimetype='text/html')
        
    except Exception as e:
        # Log the error for debugging
        error_traceback = traceback.format_exc()
        print(f"Error serving site: {str(e)}")
        print(error_traceback)
        
        # Return a generic error message
        return jsonify({
            "error": "An error occurred while serving the site. Please try again later."
        }), 500