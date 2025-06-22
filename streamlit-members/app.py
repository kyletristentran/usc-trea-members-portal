import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import hashlib
import json
import random
from typing import Dict, List, Optional

# Page configuration
st.set_page_config(
    page_title="USC TREA Members Portal",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with USC branding
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stButton>button {
        background-color: #990000;
        color: white;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #FFC72C;
        color: #1a1a1a;
    }
    .metric-card {
        background: linear-gradient(135deg, #f0f0f0 0%, #e0e0e0 100%);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left: 4px solid #990000;
    }
    h1, h2, h3 {
        color: #990000;
    }
    .stSidebar {
        background-color: #1a1a1a;
    }
    .stSidebar .markdown-text-container {
        color: white;
    }
    .success-message {
        background-color: #4ecdc4;
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .warning-message {
        background-color: #FFC72C;
        color: #1a1a1a;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state with enhanced structure
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'access_level' not in st.session_state:
    st.session_state.access_level = 'public'

# Mock database following the provided schema
class MockDatabase:
    def __init__(self):
        # Users table
        self.users = {
            1: {
                "email": "admin@usc.edu",
                "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
                "first_name": "Kyle",
                "last_name": "Tran",
                "phone": "213-555-0001",
                "created_at": datetime(2023, 1, 1),
                "last_login": datetime.now(),
                "status": "active"
            },
            2: {
                "email": "member@usc.edu",
                "password_hash": hashlib.sha256("member123".encode()).hexdigest(),
                "first_name": "Sophia",
                "last_name": "Lee",
                "phone": "213-555-0002",
                "created_at": datetime(2023, 9, 1),
                "last_login": datetime.now(),
                "status": "active"
            },
            3: {
                "email": "alumni@company.com",
                "password_hash": hashlib.sha256("alumni123".encode()).hexdigest(),
                "first_name": "Oscar",
                "last_name": "Yan",
                "phone": "213-555-0003",
                "created_at": datetime(2019, 5, 15),
                "last_login": datetime.now(),
                "status": "active"
            },
            4: {
                "email": "samantha@usc.edu",
                "password_hash": hashlib.sha256("samantha123".encode()).hexdigest(),
                "first_name": "Samantha",
                "last_name": "Armendariz",
                "phone": "213-555-0004",
                "created_at": datetime(2023, 8, 15),
                "last_login": datetime.now(),
                "status": "active"
            }
        }
        
        # Member applications
        self.member_applications = {
            1: {
                "user_id": 2,
                "graduation_year": 2025,
                "major": "Business Administration",
                "career_interests": ["Investment/REPE", "Development"],
                "application_status": "approved",
                "gpa": 3.8,
                "experience": "Summer analyst at JLL"
            },
            2: {
                "user_id": 4,
                "graduation_year": 2026,
                "major": "Real Estate Development",
                "career_interests": ["Development", "Asset Management"],
                "application_status": "approved",
                "gpa": 3.9,
                "experience": "Intern at CBRE"
            }
        }
        
        # Alumni collaborations
        self.alumni_collaborations = {
            1: {
                "user_id": 3,
                "company": "Blackstone",
                "industry": "Private Equity",
                "collaboration_type": "mentorship",
                "position": "Vice President",
                "years_experience": 8
            }
        }
        
        # User roles
        self.user_roles = {
            1: {"user_id": 1, "role_name": "admin", "permissions": ["all"]},
            2: {"user_id": 2, "role_name": "member", "permissions": ["read", "create_own"]},
            3: {"user_id": 3, "role_name": "alumni", "permissions": ["read", "collaborate"]},
            4: {"user_id": 4, "role_name": "member", "permissions": ["read", "create_own"]}
        }
        
        # Member profiles
        self.member_profiles = {
            1: {
                "user_id": 2,
                "bio": "Real estate enthusiast focused on investment analysis and financial modeling",
                "linkedin_url": "https://linkedin.com/in/sophialee",
                "experience_level": "student",
                "specializations": ["Financial Modeling", "Market Analysis"],
                "portfolio_projects": ["DCF Model for Mixed-Use Development", "LA Market Analysis Report"]
            },
            2: {
                "user_id": 3,
                "bio": "Vice President at Blackstone Real Estate with 8 years experience in acquisitions and development",
                "linkedin_url": "https://linkedin.com/in/oscaryan",
                "experience_level": "professional",
                "specializations": ["Acquisitions", "Asset Management", "Development"],
                "portfolio_projects": ["$500M Mixed-Use Acquisition", "Downtown LA Development"]
            },
            3: {
                "user_id": 4,
                "bio": "Passionate about sustainable development and ESG investing in real estate",
                "linkedin_url": "https://linkedin.com/in/samanthaarmendariz",
                "experience_level": "student",
                "specializations": ["Sustainable Development", "ESG Investing", "Development"],
                "portfolio_projects": ["Green Building Feasibility Study", "ESG Investment Framework"]
            }
        }
        
        # Resources
        self.resources = [
            {
                "resource_id": 1,
                "title": "Real Estate Financial Modeling Guide",
                "description": "Comprehensive guide to DCF analysis and property valuation",
                "file_url": "#",
                "access_level": "member",
                "created_by": 1,
                "created_at": datetime(2024, 1, 15)
            },
            {
                "resource_id": 2,
                "title": "Q4 2023 LA Market Report",
                "description": "Detailed analysis of Los Angeles commercial real estate trends",
                "file_url": "#",
                "access_level": "member",
                "created_by": 1,
                "created_at": datetime(2024, 1, 10)
            }
        ]
        
        # Events
        self.events = [
            {
                "event_id": 1,
                "title": "CBRE Campus Recruiting",
                "description": "Meet with CBRE recruiters for summer internship opportunities",
                "event_date": datetime.now() + timedelta(days=7),
                "registration_required": True,
                "max_attendees": 50,
                "current_attendees": 32,
                "location": "USC Marshall School",
                "category": "Recruiting"
            },
            {
                "event_id": 2,
                "title": "Real Estate Private Equity Panel",
                "description": "Industry leaders discuss careers in REPE",
                "event_date": datetime.now() + timedelta(days=14),
                "registration_required": True,
                "max_attendees": 100,
                "current_attendees": 67,
                "location": "Virtual Event",
                "category": "Educational"
            },
            {
                "event_id": 3,
                "title": "LA Market Deep Dive with Oscar Yan",
                "description": "Alumni Oscar Yan shares insights on LA commercial real estate trends",
                "event_date": datetime.now() + timedelta(days=21),
                "registration_required": True,
                "max_attendees": 75,
                "current_attendees": 45,
                "location": "Downtown LA",
                "category": "Networking"
            }
        ]
        
        # Job postings
        self.job_postings = [
            {
                "job_id": 1,
                "title": "Investment Analyst Intern",
                "company": "Blackstone Real Estate",
                "location": "Los Angeles, CA",
                "job_type": "Internship",
                "experience_level": "Entry Level",
                "description": "Support investment team with underwriting and due diligence",
                "requirements": ["Finance or Real Estate major", "Excel proficiency", "3.5+ GPA"],
                "salary_range": "$25-30/hour",
                "posted_by": 3,
                "posted_date": datetime.now() - timedelta(days=3),
                "application_deadline": datetime.now() + timedelta(days=14),
                "status": "active"
            },
            {
                "job_id": 2,
                "title": "Development Associate",
                "company": "Related Companies",
                "location": "Los Angeles, CA",
                "job_type": "Full-time",
                "experience_level": "Entry Level",
                "description": "Join our development team focusing on mixed-use projects",
                "requirements": ["Real Estate or related degree", "ARGUS knowledge preferred", "Strong analytical skills"],
                "salary_range": "$75,000-85,000",
                "posted_by": 1,
                "posted_date": datetime.now() - timedelta(days=5),
                "application_deadline": datetime.now() + timedelta(days=21),
                "status": "active"
            },
            {
                "job_id": 3,
                "title": "ESG Research Analyst",
                "company": "Hines",
                "location": "Los Angeles, CA",
                "job_type": "Full-time",
                "experience_level": "Entry Level",
                "description": "Focus on sustainable development and ESG metrics for real estate portfolio",
                "requirements": ["Environmental Studies or Finance background", "Passion for sustainability", "Research experience"],
                "salary_range": "$70,000-80,000",
                "posted_by": 1,
                "posted_date": datetime.now() - timedelta(days=1),
                "application_deadline": datetime.now() + timedelta(days=30),
                "status": "active"
            }
        ]
        
        # Member connections/networking
        self.member_connections = {
            2: [4],  # Sophia is connected to Samantha
            4: [2]   # Samantha is connected to Sophia
        }
        
        # Messages between members
        self.messages = [
            {
                "message_id": 1,
                "from_user": 2,
                "to_user": 4,
                "subject": "ESG Project Collaboration",
                "message": "Hi Samantha! I saw your portfolio project on ESG frameworks. Would love to collaborate on my next analysis.",
                "timestamp": datetime.now() - timedelta(hours=2),
                "read": False
            }
        ]

# Initialize mock database
db = MockDatabase()

# Authentication functions
def authenticate_user(email: str, password: str) -> Optional[Dict]:
    """Authenticate user and return user data if valid"""
    for user_id, user in db.users.items():
        if user['email'] == email:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            if user['password_hash'] == hashed_password:
                # Get role
                role_data = next((r for r in db.user_roles.values() if r['user_id'] == user_id), None)
                return {
                    'user_id': user_id,
                    'user_data': user,
                    'role': role_data['role_name'] if role_data else 'member',
                    'permissions': role_data['permissions'] if role_data else []
                }
    return None

def get_user_profile(user_id: int) -> Optional[Dict]:
    """Get user profile information"""
    return next((p for p in db.member_profiles.values() if p['user_id'] == user_id), None)

def get_user_application(user_id: int) -> Optional[Dict]:
    """Get user's member application"""
    return next((a for a in db.member_applications.values() if a['user_id'] == user_id), None)

# Intelligent matching algorithm
def match_alumni_to_members(collaboration_type: str) -> List[Dict]:
    """Match alumni opportunities with relevant members based on interests"""
    matches = []
    
    # Get all approved members
    for app_id, app in db.member_applications.items():
        if app['application_status'] == 'approved':
            user = db.users.get(app['user_id'])
            profile = get_user_profile(app['user_id'])
            
            # Simple matching based on career interests
            if collaboration_type in ['mentorship', 'consulting']:
                match_score = len(set(app['career_interests']) & {'Investment/REPE', 'Development'})
                if match_score > 0:
                    matches.append({
                        'user': user,
                        'profile': profile,
                        'application': app,
                        'match_score': match_score
                    })
    
    return sorted(matches, key=lambda x: x['match_score'], reverse=True)

# Analytics functions
def generate_member_analytics():
    """Generate analytics for the dashboard"""
    total_members = len([a for a in db.member_applications.values() if a['application_status'] == 'approved'])
    total_alumni = len(db.alumni_collaborations)
    total_resources = len(db.resources)
    upcoming_events = len([e for e in db.events if e['event_date'] > datetime.now()])
    active_jobs = len([j for j in db.job_postings if j['status'] == 'active'])
    
    return {
        'total_members': total_members,
        'total_alumni': total_alumni,
        'total_resources': total_resources,
        'upcoming_events': upcoming_events,
        'active_jobs': active_jobs,
        'member_growth': 23,  # Mock data
        'engagement_rate': 78,  # Mock data
        'job_placement_rate': 85,
        'mentor_matches': 15
    }

def get_user_messages(user_id: int, unread_only: bool = False) -> List[Dict]:
    """Get messages for a specific user"""
    user_messages = [m for m in db.messages if m['to_user'] == user_id]
    if unread_only:
        user_messages = [m for m in user_messages if not m['read']]
    return sorted(user_messages, key=lambda x: x['timestamp'], reverse=True)

def get_job_applications(user_id: int) -> List[Dict]:
    """Get job applications for a user (mock data)"""
    return [
        {"job_id": 1, "company": "Blackstone", "position": "Investment Analyst Intern", 
         "status": "Under Review", "applied_date": datetime.now() - timedelta(days=5)},
        {"job_id": 2, "company": "Related Companies", "position": "Development Associate", 
         "status": "Interview Scheduled", "applied_date": datetime.now() - timedelta(days=8)}
    ]

# Sidebar with role-based navigation
with st.sidebar:
    st.image("https://via.placeholder.com/200x80/990000/FFFFFF?text=USC+TREA", width=200)
    
    if st.session_state.logged_in:
        st.markdown(f"### Welcome, {st.session_state.user_data['first_name']}!")
        st.markdown(f"**Role:** {st.session_state.user_role.title()}")
        st.markdown(f"**Status:** {st.session_state.user_data['status'].title()}")
        
        st.markdown("---")
        
        # Role-based navigation
        if st.session_state.user_role == 'admin':
            page = st.selectbox(
                "Navigate",
                ["Admin Dashboard", "Member Management", "Application Review", 
                 "Alumni Relations", "Resources", "Events", "Analytics", "Settings"]
            )
        elif st.session_state.user_role == 'alumni':
            page = st.selectbox(
                "Navigate",
                ["Alumni Dashboard", "Collaboration Hub", "Member Directory", 
                 "Events", "Resources", "Profile"]
            )
        else:  # member
            page = st.selectbox(
                "Navigate",
                ["Member Dashboard", "Job Board", "Portfolio", "Resources", "Events", 
                 "Directory", "Networking", "Profile"]
            )
        
        if st.button("Logout", use_container_width=True):
            for key in ['logged_in', 'user_data', 'user_id', 'user_role', 'access_level']:
                if key in st.session_state:
                    st.session_state[key] = None if key != 'logged_in' else False
            st.rerun()
    else:
        st.markdown("### Login to Portal")

# Main content area
if not st.session_state.logged_in:
    # Enhanced login page
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("# USC TREA Members Portal")
        st.markdown("### Access exclusive resources and connect with the TREA community")
        
        tab1, tab2 = st.tabs(["Login", "About Portal"])
        
        with tab1:
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="your.email@usc.edu")
                password = st.text_input("Password", type="password")
                remember_me = st.checkbox("Remember me")
                
                col1, col2 = st.columns(2)
                with col1:
                    submit = st.form_submit_button("Login", use_container_width=True)
                with col2:
                    demo = st.form_submit_button("Demo Access", use_container_width=True)
                
                if submit:
                    auth_result = authenticate_user(email, password)
                    if auth_result:
                        st.session_state.logged_in = True
                        st.session_state.user_id = auth_result['user_id']
                        st.session_state.user_data = auth_result['user_data']
                        st.session_state.user_role = auth_result['role']
                        st.session_state.access_level = 'admin' if auth_result['role'] == 'admin' else 'member'
                        
                        # Update last login
                        db.users[auth_result['user_id']]['last_login'] = datetime.now()
                        
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Please try again.")
                
                if demo:
                    st.info("Demo Accounts Available:")
                    st.code("""
Admin: admin@usc.edu / admin123
Member: member@usc.edu / member123
Alumni: alumni@company.com / alumni123
                    """)
        
        with tab2:
            st.markdown("""
            ### Portal Features by Role
            
            **Members:**
            - Access exclusive resources and market reports
            - Browse job opportunities
            - Register for events
            - Connect with alumni mentors
            
            **Alumni:**
            - Offer mentorship and guidance
            - Post job opportunities
            - Share industry insights
            - Participate in events
            
            **Administrators:**
            - Manage member applications
            - Oversee alumni relations
            - Upload resources
            - Analytics and reporting
            """)

else:
    # Logged in content based on role
    if 'page' not in locals():
        page = "Member Dashboard"
    
    # Admin Pages
    if st.session_state.user_role == 'admin' and page == "Admin Dashboard":
        st.title("Admin Dashboard")
        
        # Analytics metrics
        analytics = generate_member_analytics()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Active Members", analytics['total_members'], f"+{analytics['member_growth']} this month")
        with col2:
            st.metric("Alumni Partners", analytics['total_alumni'], "+5 this quarter")
        with col3:
            st.metric("Active Jobs", analytics['active_jobs'], "+2 this week")
        with col4:
            st.metric("Placement Rate", f"{analytics['job_placement_rate']}%", "+3%")
        with col5:
            st.metric("Mentor Matches", analytics['mentor_matches'], "+2 this month")
        
        st.markdown("---")
        
        # Recent activity
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Recent Applications")
            applications_df = pd.DataFrame([
                {"Name": "Kyle Tran", "Year": "2026", "Status": "Pending", "Date": "2024-01-20"},
                {"Name": "Sophia Lee", "Year": "2025", "Status": "Pending", "Date": "2024-01-19"},
                {"Name": "Oscar Yan", "Year": "2027", "Status": "Approved", "Date": "2024-01-18"},
            ])
            st.dataframe(applications_df, use_container_width=True)
        
        with col2:
            st.subheader("Upcoming Events")
            for event in db.events[:3]:
                with st.container():
                    st.markdown(f"**{event['title']}**")
                    st.caption(f"{event['event_date'].strftime('%B %d, %Y')} | {event['current_attendees']}/{event['max_attendees']} registered")
                    st.progress(event['current_attendees'] / event['max_attendees'])
        
        # Advanced analytics section
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Member Growth Trend")
            dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='M')
            growth_data = pd.DataFrame({
                'Date': dates,
                'Members': [350 + i*5 + random.randint(-10, 20) for i in range(len(dates))],
                'Alumni': [150 + i*2 + random.randint(-5, 10) for i in range(len(dates))]
            })
            
            fig = px.line(growth_data, x='Date', y=['Members', 'Alumni'],
                         title="Membership Growth Over Time")
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Job Placement Analysis")
            placement_data = pd.DataFrame({
                'Company Type': ['Investment/REPE', 'Development', 'Brokerage', 'Consulting', 'Other'],
                'Placements': [15, 12, 8, 5, 3]
            })
            
            fig2 = px.pie(placement_data, values='Placements', names='Company Type',
                         title="Job Placements by Industry")
            fig2.update_layout(height=350)
            st.plotly_chart(fig2, use_container_width=True)
        
        # Engagement metrics
        st.markdown("---")
        st.subheader("Member Engagement Analytics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Event attendance
            event_data = pd.DataFrame({
                'Event': ['CBRE Recruiting', 'REPE Panel', 'Market Deep Dive', 'Networking', 'Workshop'],
                'Attendance': [32, 67, 45, 28, 22]
            })
            fig3 = px.bar(event_data, x='Event', y='Attendance', title="Event Attendance")
            fig3.update_layout(height=300)
            st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            # Resource downloads
            resource_data = pd.DataFrame({
                'Resource Type': ['Models', 'Reports', 'Guides', 'Templates'],
                'Downloads': [145, 89, 67, 34]
            })
            fig4 = px.bar(resource_data, x='Resource Type', y='Downloads', title="Resource Downloads")
            fig4.update_layout(height=300)
            st.plotly_chart(fig4, use_container_width=True)
        
        with col3:
            # Member activity heatmap data
            activity_data = pd.DataFrame({
                'Day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                'Logins': [45, 52, 48, 55, 42, 18, 12]
            })
            fig5 = px.bar(activity_data, x='Day', y='Logins', title="Daily Login Activity")
            fig5.update_layout(height=300)
            st.plotly_chart(fig5, use_container_width=True)
        
        # Geographic distribution
        st.markdown("---")
        st.subheader("Member Geographic Distribution")
        
        geo_data = pd.DataFrame({
            'Location': ['Los Angeles', 'San Francisco', 'New York', 'Chicago', 'Seattle', 'Other'],
            'Members': [45, 12, 8, 5, 3, 7],
            'Alumni': [15, 8, 12, 6, 4, 5]
        })
        
        fig6 = px.bar(geo_data, x='Location', y=['Members', 'Alumni'], 
                     title="Member Distribution by Location", barmode='group')
        fig6.update_layout(height=400)
        st.plotly_chart(fig6, use_container_width=True)
    
    elif st.session_state.user_role == 'admin' and page == "Member Management":
        st.title("Member Management")
        
        # Search and filters
        col1, col2, col3 = st.columns(3)
        with col1:
            search = st.text_input("Search members", placeholder="Name or email...")
        with col2:
            status_filter = st.selectbox("Status", ["All", "Active", "Inactive", "Pending"])
        with col3:
            year_filter = st.selectbox("Graduation Year", ["All", "2025", "2026", "2027", "2028"])
        
        # Member table
        members_data = []
        for user_id, user in db.users.items():
            app = get_user_application(user_id)
            if app:
                members_data.append({
                    "Name": f"{user['first_name']} {user['last_name']}",
                    "Email": user['email'],
                    "Year": app['graduation_year'],
                    "Major": app['major'],
                    "Status": user['status'].title(),
                    "Joined": user['created_at'].strftime('%Y-%m-%d')
                })
        
        if members_data:
            df = pd.DataFrame(members_data)
            st.dataframe(df, use_container_width=True)
            
            # Bulk actions
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Export to CSV"):
                    st.download_button(
                        label="Download CSV",
                        data=df.to_csv(index=False),
                        file_name=f"trea_members_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
    
    elif st.session_state.user_role == 'admin' and page == "Application Review":
        st.title("Application Review")
        
        # Pending applications
        st.subheader("Pending Applications")
        
        # Mock pending applications
        pending_apps = [
            {
                "id": 1,
                "name": "Kyle Tran",
                "email": "ktran@usc.edu",
                "year": 2026,
                "major": "Finance",
                "gpa": 3.8,
                "interests": ["Investment/REPE", "Development"],
                "experience": "Summer analyst at JLL",
                "submitted": datetime.now() - timedelta(days=2)
            },
            {
                "id": 2,
                "name": "Sophia Lee",
                "email": "slee@usc.edu",
                "year": 2025,
                "major": "Real Estate Development",
                "gpa": 3.6,
                "interests": ["Development", "Asset Management"],
                "experience": "Research assistant",
                "submitted": datetime.now() - timedelta(days=3)
            }
        ]
        
        for app in pending_apps:
            with st.expander(f"{app['name']} - {app['year']} ({app['submitted'].strftime('%Y-%m-%d')})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Personal Information**")
                    st.write(f"Email: {app['email']}")
                    st.write(f"Major: {app['major']}")
                    st.write(f"GPA: {app['gpa']}")
                
                with col2:
                    st.markdown("**Career Interests**")
                    st.write("Areas: " + ", ".join(app['interests']))
                    st.write(f"Experience: {app['experience']}")
                
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"Approve", key=f"approve_{app['id']}"):
                        st.success(f"Approved {app['name']}'s application")
                with col2:
                    if st.button(f"Request Info", key=f"info_{app['id']}"):
                        st.info("Email sent requesting additional information")
                with col3:
                    if st.button(f"Reject", key=f"reject_{app['id']}"):
                        st.error(f"Rejected {app['name']}'s application")
    
    # Alumni Pages
    elif st.session_state.user_role == 'alumni' and page == "Alumni Dashboard":
        st.title("Alumni Dashboard")
        
        profile = get_user_profile(st.session_state.user_id)
        
        # Welcome message
        st.markdown(f"### Welcome back, {st.session_state.user_data['first_name']}!")
        st.markdown(f"Thank you for being part of the TREA alumni network.")
        
        # Collaboration stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Students Mentored", "12", "+3 this semester")
        with col2:
            st.metric("Events Participated", "5", "+1 upcoming")
        with col3:
            st.metric("Job Posts", "3", "2 filled")
        
        st.markdown("---")
        
        # Current collaborations
        st.subheader("Your Active Collaborations")
        
        collab_data = pd.DataFrame([
            {"Type": "Mentorship", "Students": 3, "Status": "Active", "Started": "2024-01-01"},
            {"Type": "Guest Speaking", "Event": "REPE Panel", "Date": "2024-02-15", "Status": "Scheduled"},
        ])
        st.dataframe(collab_data, use_container_width=True)
        
        # Quick actions
        st.subheader("Quick Actions")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Post Job Opportunity", use_container_width=True):
                st.session_state.show_job_form = True
        with col2:
            if st.button("Schedule Speaking Event", use_container_width=True):
                st.session_state.show_event_form = True
        with col3:
            if st.button("Update Availability", use_container_width=True):
                st.session_state.show_availability = True
    
    elif st.session_state.user_role == 'alumni' and page == "Collaboration Hub":
        st.title("Collaboration Hub")
        
        st.markdown("### Matched Students Based on Your Expertise")
        
        # Get matched students
        matches = match_alumni_to_members('mentorship')
        
        if matches:
            for match in matches[:5]:  # Show top 5 matches
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 1])
                    
                    with col1:
                        st.markdown(f"**{match['user']['first_name']} {match['user']['last_name']}**")
                        st.caption(f"Class of {match['application']['graduation_year']} | {match['application']['major']}")
                        st.write("Interests: " + ", ".join(match['application']['career_interests']))
                    
                    with col2:
                        st.write(f"Match Score: {'⭐' * match['match_score']}")
                        if match['profile']:
                            st.caption(match['profile']['bio'][:100] + "...")
                    
                    with col3:
                        if st.button("Connect", key=f"connect_{match['user']['email']}"):
                            st.success("Connection request sent!")
                    
                    st.markdown("---")
    
    # Member Pages
    elif st.session_state.user_role == 'member' and page == "Member Dashboard":
        st.title("Member Dashboard")
        
        st.markdown(f"### Welcome, {st.session_state.user_data['first_name']}!")
        
        # Member metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Events Attended", "8", "+2 this month")
        with col2:
            st.metric("Resources Accessed", "23", "+5 this week")
        with col3:
            st.metric("Connections", "15", "+3 new")
        with col4:
            st.metric("Profile Views", "47", "+12 this week")
        
        st.markdown("---")
        
        # Upcoming events
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📅 Upcoming Events")
            for event in db.events[:2]:
                with st.container():
                    st.markdown(f"**{event['title']}**")
                    st.caption(event['description'][:100] + "...")
                    st.write(f"📍 {event['event_date'].strftime('%B %d at %I:%M %p')}")
                    if st.button(f"Register", key=f"reg_{event['event_id']}"):
                        st.success("Registered successfully!")
        
        with col2:
            st.subheader("📚 Latest Resources")
            for resource in db.resources[:2]:
                with st.container():
                    st.markdown(f"**{resource['title']}**")
                    st.caption(resource['description'][:100] + "...")
                    if st.button(f"Download", key=f"dl_{resource['resource_id']}"):
                        st.info("Download started...")
        
        # Recommendations
        st.markdown("---")
        st.subheader("🎯 Recommended for You")
        
        rec_tabs = st.tabs(["Alumni Mentors", "Job Opportunities", "Learning Paths"])
        
        with rec_tabs[0]:
            st.info("Based on your interest in Investment/REPE, connect with these alumni:")
            alumni_recs = [
                {"name": "Oscar Yan", "company": "Blackstone", "role": "VP"},
                {"name": "Samantha Armendariz", "company": "Hines", "role": "Associate"},
            ]
            for alum in alumni_recs:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{alum['name']}** - {alum['role']} at {alum['company']}")
                with col2:
                    st.button("Connect", key=f"alum_{alum['name']}")
        
        with rec_tabs[1]:
            st.info("New opportunities matching your profile:")
            for job in db.job_postings[:2]:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"**{job['title']}** at {job['company']}")
                    st.caption(f"{job['location']} • {job['salary_range']} • Posted {job['posted_date'].strftime('%m/%d')}") 
                with col2:
                    if st.button("Apply", key=f"apply_{job['job_id']}"):
                        st.success("Application submitted!")
        
        with rec_tabs[2]:
            st.info("Recommended courses based on your interests:")
            courses = ["Real Estate Financial Modeling", "Market Analysis Fundamentals", "ARGUS Certification Prep"]
            for course in courses:
                st.write(f"• {course}")
    
    elif page == "Job Board":
        st.title("🎯 Job Board")
        
        # Job filters
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            job_type_filter = st.selectbox("Job Type", ["All", "Internship", "Full-time", "Part-time"])
        with col2:
            experience_filter = st.selectbox("Experience", ["All", "Entry Level", "Mid Level", "Senior Level"])
        with col3:
            location_filter = st.selectbox("Location", ["All", "Los Angeles", "New York", "San Francisco", "Chicago"])
        with col4:
            company_filter = st.text_input("Company Search", placeholder="Search companies...")
        
        # My Applications section
        with st.expander("📋 My Applications", expanded=False):
            user_applications = get_job_applications(st.session_state.user_id)
            if user_applications:
                for app in user_applications:
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.write(f"**{app['position']}** at {app['company']}")
                    with col2:
                        status_color = "🟢" if app['status'] == "Interview Scheduled" else "🟡"
                        st.write(f"{status_color} {app['status']}")
                    with col3:
                        st.caption(f"Applied {app['applied_date'].strftime('%m/%d/%y')}")
                    st.markdown("---")
            else:
                st.info("No applications yet. Start applying to jobs below!")
        
        st.markdown("### Available Positions")
        
        # Job listings
        for job in db.job_postings:
            # Apply filters
            if job_type_filter != "All" and job['job_type'] != job_type_filter:
                continue
            if experience_filter != "All" and job['experience_level'] != experience_filter:
                continue
            if location_filter != "All" and location_filter.lower() not in job['location'].lower():
                continue
            if company_filter and company_filter.lower() not in job['company'].lower():
                continue
            
            with st.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown(f"### {job['title']}")
                    st.markdown(f"**{job['company']}** • {job['location']} • {job['job_type']}")
                    st.write(job['description'])
                    
                    # Requirements
                    st.markdown("**Requirements:**")
                    for req in job['requirements']:
                        st.write(f"• {req}")
                    
                    # Job details
                    col1a, col1b, col1c = st.columns(3)
                    with col1a:
                        st.caption(f"💰 {job['salary_range']}")
                    with col1b:
                        st.caption(f"📅 Posted {job['posted_date'].strftime('%B %d, %Y')}")
                    with col1c:
                        st.caption(f"⏰ Apply by {job['application_deadline'].strftime('%B %d, %Y')}")
                
                with col2:
                    if st.button("Apply Now", key=f"apply_job_{job['job_id']}", use_container_width=True):
                        st.success("Application submitted successfully!")
                        st.balloons()
                    
                    if st.button("Save Job", key=f"save_job_{job['job_id']}", use_container_width=True):
                        st.info("Job saved to your list")
                    
                    st.button("Share", key=f"share_job_{job['job_id']}", use_container_width=True)
                
                st.markdown("---")
    
    elif page == "Portfolio":
        st.title("📁 My Portfolio")
        
        profile = get_user_profile(st.session_state.user_id)
        
        # Upload new project
        with st.expander("➕ Add New Project", expanded=False):
            with st.form("new_project_form"):
                project_title = st.text_input("Project Title")
                project_type = st.selectbox("Project Type", ["Financial Model", "Market Analysis", "Research Paper", "Case Study", "Development Proposal"])
                project_description = st.text_area("Description", height=100)
                project_file = st.file_uploader("Upload File", type=['pdf', 'xlsx', 'docx', 'pptx'])
                project_tags = st.multiselect("Tags", ["DCF", "Market Analysis", "Development", "Investment", "ESG", "Sustainability", "ARGUS", "Research"])
                
                if st.form_submit_button("Add Project", use_container_width=True):
                    if project_title and project_description:
                        st.success(f"Project '{project_title}' added to your portfolio!")
                    else:
                        st.error("Please fill in all required fields")
        
        # Current portfolio projects
        st.markdown("### My Projects")
        
        if profile and 'portfolio_projects' in profile:
            # Mock detailed project data
            project_details = {
                "DCF Model for Mixed-Use Development": {
                    "type": "Financial Model",
                    "description": "Comprehensive DCF analysis for a 200-unit mixed-use development in downtown LA",
                    "date": "January 2024",
                    "tags": ["DCF", "Development", "Mixed-Use"],
                    "views": 47,
                    "downloads": 12
                },
                "LA Market Analysis Report": {
                    "type": "Market Analysis", 
                    "description": "Quarterly analysis of Los Angeles commercial real estate market trends and forecasts",
                    "date": "December 2023",
                    "tags": ["Market Analysis", "LA Market", "Research"],
                    "views": 89,
                    "downloads": 25
                },
                "Green Building Feasibility Study": {
                    "type": "Research Paper",
                    "description": "Analysis of LEED certification costs vs. long-term benefits for office buildings",
                    "date": "November 2023", 
                    "tags": ["ESG", "Sustainability", "Research"],
                    "views": 63,
                    "downloads": 18
                },
                "ESG Investment Framework": {
                    "type": "Case Study",
                    "description": "Framework for integrating ESG metrics into real estate investment decisions",
                    "date": "October 2023",
                    "tags": ["ESG", "Investment", "Framework"],
                    "views": 72,
                    "downloads": 31
                }
            }
            
            for project_name in profile['portfolio_projects']:
                if project_name in project_details:
                    details = project_details[project_name]
                    
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"### {project_name}")
                            st.markdown(f"**{details['type']}** • {details['date']}")
                            st.write(details['description'])
                            
                            # Tags
                            tag_cols = st.columns(len(details['tags']))
                            for i, tag in enumerate(details['tags']):
                                with tag_cols[i]:
                                    st.markdown(f"`{tag}`")
                        
                        with col2:
                            st.metric("Views", details['views'])
                            st.metric("Downloads", details['downloads'])
                            
                            if st.button("Edit", key=f"edit_{project_name}"):
                                st.info("Edit mode activated")
                            if st.button("Share", key=f"share_proj_{project_name}"):
                                st.success("Share link copied!")
                        
                        st.markdown("---")
        else:
            st.info("No projects in your portfolio yet. Add your first project above!")
        
        # Portfolio analytics
        st.markdown("### Portfolio Analytics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Projects", "4")
        with col2:
            st.metric("Total Views", "271", "+15 this week")
        with col3:
            st.metric("Total Downloads", "86", "+8 this week")
        with col4:
            st.metric("Profile Ranking", "#12", "+3 positions")
    
    elif page == "Networking":
        st.title("🤝 Networking Hub")
        
        # Unread messages notification
        unread_messages = get_user_messages(st.session_state.user_id, unread_only=True)
        if unread_messages:
            st.warning(f"You have {len(unread_messages)} unread messages!")
        
        tab1, tab2, tab3 = st.tabs(["Messages", "My Connections", "Discover Members"])
        
        with tab1:
            st.subheader("💬 Messages")
            
            # Message composition
            with st.expander("✉️ Compose New Message", expanded=False):
                with st.form("compose_message"):
                    to_user = st.selectbox("To:", ["Samantha Armendariz", "Oscar Yan", "Kyle Tran"])
                    subject = st.text_input("Subject")
                    message_body = st.text_area("Message", height=100)
                    
                    if st.form_submit_button("Send Message"):
                        if subject and message_body:
                            st.success(f"Message sent to {to_user}!")
                        else:
                            st.error("Please fill in all fields")
            
            # Message inbox
            st.markdown("### Inbox")
            all_messages = get_user_messages(st.session_state.user_id)
            
            if all_messages:
                for msg in all_messages:
                    sender = db.users.get(msg['from_user'], {}).get('first_name', 'Unknown') 
                    sender_last = db.users.get(msg['from_user'], {}).get('last_name', '')
                    
                    with st.expander(f"{'🔴' if not msg['read'] else '📧'} From {sender} {sender_last}: {msg['subject']}"):
                        st.write(f"**Sent:** {msg['timestamp'].strftime('%B %d, %Y at %I:%M %p')}")
                        st.write(msg['message'])
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Reply", key=f"reply_{msg['message_id']}"):
                                st.info("Reply window opened")
                        with col2:
                            if not msg['read'] and st.button("Mark as Read", key=f"read_{msg['message_id']}"):
                                msg['read'] = True
                                st.success("Message marked as read")
            else:
                st.info("No messages yet. Start networking to receive messages!")
        
        with tab2:
            st.subheader("👥 My Connections")
            
            # Connection stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Connections", "15", "+3 this month")
            with col2:
                st.metric("Alumni Mentors", "3", "+1 new")
            with col3:
                st.metric("Peer Connections", "12", "+2 this month")
            
            # Current connections
            user_connections = db.member_connections.get(st.session_state.user_id, [])
            
            if user_connections:
                for connection_id in user_connections:
                    connection_user = db.users.get(connection_id)
                    connection_profile = get_user_profile(connection_id)
                    
                    if connection_user and connection_profile:
                        with st.container():
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown(f"**{connection_user['first_name']} {connection_user['last_name']}**")
                                st.caption(connection_profile.get('bio', 'No bio available')[:100] + "...")
                                
                                # Show specializations
                                if connection_profile.get('specializations'):
                                    spec_text = "Specializes in: " + ", ".join(connection_profile['specializations'][:3])
                                    st.write(spec_text)
                            
                            with col2:
                                if st.button("Message", key=f"msg_conn_{connection_id}"):
                                    st.info("Message window opened")
                                if st.button("View Profile", key=f"view_conn_{connection_id}"):
                                    st.info("Profile opened")
                            
                            st.markdown("---")
            else:
                st.info("No connections yet. Discover new members in the next tab!")
        
        with tab3:
            st.subheader("🔍 Discover Members")
            
            # Search filters
            col1, col2, col3 = st.columns(3)
            with col1:
                experience_level = st.selectbox("Experience Level", ["All", "Student", "Professional", "Alumni"])
            with col2:
                specialization = st.selectbox("Specialization", ["All", "Financial Modeling", "Development", "Investment", "ESG", "Market Analysis"])
            with col3:
                graduation_year = st.selectbox("Class Year", ["All", "2024", "2025", "2026", "2027", "Alumni"])
            
            # Member recommendations
            st.markdown("### Recommended Connections")
            
            # Show other members (excluding current user)
            for user_id, user in db.users.items():
                if user_id == st.session_state.user_id:  # Skip current user
                    continue
                    
                profile = get_user_profile(user_id)
                if not profile:
                    continue
                
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        st.markdown(f"### {user['first_name']} {user['last_name']}")
                        st.write(profile.get('bio', 'No bio available'))
                        
                        if profile.get('specializations'):
                            st.write("**Specializations:** " + ", ".join(profile['specializations']))
                        
                        if profile.get('portfolio_projects'):
                            st.write(f"**Portfolio:** {len(profile['portfolio_projects'])} projects")
                    
                    with col2:
                        if st.button("Connect", key=f"connect_{user_id}", use_container_width=True):
                            st.success(f"Connection request sent to {user['first_name']}!")
                        
                        if st.button("View Profile", key=f"view_{user_id}", use_container_width=True):
                            st.info("Profile opened")
                    
                    st.markdown("---")
    
    elif page == "Resources":
        st.title("Resources Library")
        
        # Resource categories
        category = st.selectbox("Category", ["All", "Market Reports", "Guides", "Templates", "Industry Research"])
        
        # Search
        search = st.text_input("Search resources", placeholder="Search by title or keyword...")
        
        # Resource grid
        col1, col2 = st.columns(2)
        
        for i, resource in enumerate(db.resources):
            with col1 if i % 2 == 0 else col2:
                with st.container():
                    st.markdown(f"### {resource['title']}")
                    st.caption(f"Added {resource['created_at'].strftime('%B %d, %Y')}")
                    st.write(resource['description'])
                    
                    if st.session_state.access_level in ['admin', 'member']:
                        if st.button(f"Access Resource", key=f"resource_{resource['resource_id']}"):
                            st.success("Resource opened in new tab")
                    else:
                        st.warning("Premium membership required")
                    
                    st.markdown("---")
    
    elif page == "Events":
        st.title("Events Calendar")
        
        # Event filters
        col1, col2, col3 = st.columns(3)
        with col1:
            event_type = st.selectbox("Event Type", ["All", "Recruiting", "Networking", "Educational", "Social"])
        with col2:
            timeframe = st.selectbox("Timeframe", ["Upcoming", "This Month", "Next Month", "Past Events"])
        with col3:
            if st.button("Add to Calendar", use_container_width=True):
                st.info("Calendar integration coming soon!")
        
        # Events list
        for event in db.events:
            with st.expander(f"{event['title']} - {event['event_date'].strftime('%B %d, %Y')}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Description:** {event['description']}")
                    st.write(f"📅 **Date:** {event['event_date'].strftime('%A, %B %d at %I:%M %p')}")
                    st.write(f"👥 **Registered:** {event['current_attendees']}/{event['max_attendees']}")
                    
                    # Progress bar for registration
                    st.progress(event['current_attendees'] / event['max_attendees'])
                
                with col2:
                    if event['current_attendees'] < event['max_attendees']:
                        if st.button("Register", key=f"event_reg_{event['event_id']}"):
                            st.success("Successfully registered!")
                            event['current_attendees'] += 1
                            st.rerun()
                    else:
                        st.error("Event Full")
                        if st.button("Join Waitlist", key=f"waitlist_{event['event_id']}"):
                            st.info("Added to waitlist")
    
    elif page == "Directory":
        st.title("👥 Member Directory")
        
        # Search and filter options
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            name_search = st.text_input("Search by name", placeholder="Enter name...")
        with col2:
            class_filter = st.selectbox("Class Year", ["All", "2024", "2025", "2026", "2027", "Alumni"])
        with col3:
            specialization_filter = st.selectbox("Specialization", ["All", "Financial Modeling", "Development", "Investment", "ESG", "Market Analysis"])
        with col4:
            sort_by = st.selectbox("Sort by", ["Name", "Class Year", "Join Date", "Connections"])
        
        st.markdown("---")
        
        # Member cards
        members_shown = 0
        for user_id, user in db.users.items():
            profile = get_user_profile(user_id)
            application = get_user_application(user_id)
            
            if not profile:  # Skip if no profile
                continue
                
            # Apply filters
            if name_search and name_search.lower() not in f"{user['first_name']} {user['last_name']}".lower():
                continue
                
            if class_filter != "All":
                if application and str(application.get('graduation_year', '')) != class_filter:
                    continue
                elif not application and class_filter != "Alumni":
                    continue
            
            if specialization_filter != "All" and profile.get('specializations'):
                if specialization_filter not in profile['specializations']:
                    continue
            
            # Display member card
            with st.container():
                col1, col2, col3 = st.columns([1, 3, 1])
                
                with col1:
                    # Profile picture placeholder
                    st.image(f"https://ui-avatars.com/api/?name={user['first_name']}+{user['last_name']}&background=990000&color=fff&size=100", width=100)
                
                with col2:
                    st.markdown(f"### {user['first_name']} {user['last_name']}")
                    
                    if application:
                        st.caption(f"Class of {application['graduation_year']} • {application['major']}")
                    else:
                        st.caption("Alumni")
                    
                    st.write(profile.get('bio', 'No bio available')[:120] + "...")
                    
                    if profile.get('specializations'):
                        spec_tags = " ".join([f"`{spec}`" for spec in profile['specializations'][:3]])
                        st.markdown(spec_tags)
                    
                    # Portfolio count
                    if profile.get('portfolio_projects'):
                        st.caption(f"📁 {len(profile['portfolio_projects'])} projects")
                
                with col3:
                    if st.button("View Profile", key=f"view_profile_{user_id}", use_container_width=True):
                        st.info(f"Viewing {user['first_name']}'s profile")
                    
                    if user_id != st.session_state.user_id:
                        if st.button("Connect", key=f"connect_dir_{user_id}", use_container_width=True):
                            st.success(f"Connection request sent to {user['first_name']}!")
                        
                        if st.button("Message", key=f"message_dir_{user_id}", use_container_width=True):
                            st.info(f"Message window opened for {user['first_name']}")
                
                st.markdown("---")
                members_shown += 1
        
        if members_shown == 0:
            st.info("No members found matching your search criteria.")
        else:
            st.caption(f"Showing {members_shown} members")
    
    elif page in ["Profile", "Settings"]:
        st.title("Profile Settings")
        
        tabs = st.tabs(["Profile", "Account", "Notifications", "Privacy"])
        
        with tabs[0]:
            st.subheader("Profile Information")
            
            profile = get_user_profile(st.session_state.user_id)
            
            with st.form("profile_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    first_name = st.text_input("First Name", value=st.session_state.user_data['first_name'])
                    last_name = st.text_input("Last Name", value=st.session_state.user_data['last_name'])
                    phone = st.text_input("Phone", value=st.session_state.user_data['phone'])
                
                with col2:
                    email = st.text_input("Email", value=st.session_state.user_data['email'], disabled=True)
                    linkedin = st.text_input("LinkedIn URL", value=profile['linkedin_url'] if profile else "")
                    
                bio = st.text_area("Bio", value=profile['bio'] if profile else "", height=100)
                
                if profile:
                    specializations = st.multiselect(
                        "Areas of Expertise",
                        ["Financial Modeling", "Market Analysis", "Development", "Asset Management", 
                         "Acquisitions", "Property Management", "Consulting"],
                        default=profile['specializations']
                    )
                
                if st.form_submit_button("Update Profile", use_container_width=True):
                    st.success("Profile updated successfully!")
        
        with tabs[1]:
            st.subheader("Account Settings")
            
            # Account info
            st.write(f"**Member Since:** {st.session_state.user_data['created_at'].strftime('%B %Y')}")
            st.write(f"**Last Login:** {st.session_state.user_data['last_login'].strftime('%B %d, %Y at %I:%M %p')}")
            st.write(f"**Account Status:** {st.session_state.user_data['status'].title()}")
            
            st.markdown("---")
            
            # Password change
            with st.form("password_form"):
                st.subheader("Change Password")
                current_password = st.text_input("Current Password", type="password")
                new_password = st.text_input("New Password", type="password")
                confirm_password = st.text_input("Confirm New Password", type="password")
                
                if st.form_submit_button("Update Password"):
                    if new_password == confirm_password:
                        st.success("Password updated successfully!")
                    else:
                        st.error("Passwords do not match")
        
        with tabs[2]:
            st.subheader("Notification Preferences")
            
            st.checkbox("Email notifications for new job postings", value=True)
            st.checkbox("Weekly newsletter", value=True)
            st.checkbox("Event reminders", value=True)
            st.checkbox("Alumni connection requests", value=True)
            st.checkbox("Resource updates", value=False)
            st.checkbox("System announcements", value=True)
            
            if st.button("Save Preferences", use_container_width=True):
                st.success("Notification preferences updated!")
        
        with tabs[3]:
            st.subheader("Privacy Settings")
            
            st.checkbox("Show profile in member directory", value=True)
            st.checkbox("Allow other members to contact me", value=True)
            st.checkbox("Show my career interests to alumni", value=True)
            st.checkbox("Include me in alumni matching", value=True)
            
            st.markdown("---")
            
            st.subheader("Data Management")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Download My Data", use_container_width=True):
                    st.info("Your data export will be emailed to you within 24 hours")
            with col2:
                if st.button("Delete Account", use_container_width=True, type="secondary"):
                    st.warning("Please contact admin@usctrea.com to delete your account")