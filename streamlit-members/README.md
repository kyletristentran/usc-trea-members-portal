# USC TREA Members Portal

A comprehensive member management and networking platform for the USC Trojan Real Estate Association (TREA). This enhanced Streamlit application provides a centralized hub for students, alumni, and administrators to connect, share resources, and advance careers in real estate.

## < Features

### For Members (Students)
- **=Ê Enhanced Dashboard**: Personalized metrics, recommendations, and activity tracking
- **<¯ Job Board**: Comprehensive job listings with advanced filtering and application tracking
- **=Á Portfolio Showcase**: Upload and showcase projects, track views and downloads
- **> Networking Hub**: Connect with peers and alumni, send messages, discover new connections
- **=Ú Resource Library**: Access exclusive guides, reports, and templates
- **=Å Event Management**: Register for events, view attendance, and track participation
- **=e Member Directory**: Search and filter members by specialization, class year, and interests

### For Alumni
- **<â Alumni Dashboard**: Track mentorship impact and collaboration opportunities
- **> Collaboration Hub**: Get matched with students based on expertise and interests
- **=¼ Job Posting**: Post opportunities and track applications
- **<¤ Speaking Opportunities**: Schedule and manage speaking engagements
- **=È Impact Tracking**: Monitor students mentored and placement success

### For Administrators
- **=' Admin Dashboard**: Comprehensive analytics and member management
- **=Ê Advanced Analytics**: Detailed insights on member engagement, job placements, and growth
- **=h<“ Application Review**: Streamlined member application processing
- **=È Performance Metrics**: Track KPIs, financial performance, and member satisfaction
- **<â Alumni Relations**: Manage alumni partnerships and collaborations

## =€ Quick Start

### Prerequisites
- Python 3.11+
- UV package manager (recommended) or pip

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd streamlit-members
```

2. Install dependencies using UV:
```bash
uv pip install -r pyproject.toml
```

Or using pip:
```bash
pip install streamlit pandas plotly numpy Pillow
```

### Running the Application

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

## = Demo Accounts

For testing and demonstration purposes, use these accounts:

| Role | Email | Password | Name |
|------|--------|-----------|------|
| Admin | admin@usc.edu | admin123 | Kyle Tran |
| Member | member@usc.edu | member123 | Sophia Lee |
| Alumni | alumni@company.com | alumni123 | Oscar Yan |
| Member | samantha@usc.edu | samantha123 | Samantha Armendariz |

## <× Architecture

### Data Structure
The application uses a mock database with the following entities:
- **Users**: Basic user information and authentication
- **Member Applications**: Academic and career interest data
- **Member Profiles**: Detailed profiles with bios, specializations, and portfolios
- **Alumni Collaborations**: Industry experience and collaboration preferences
- **Job Postings**: Comprehensive job listings with requirements and deadlines
- **Events**: TREA events with registration and attendance tracking
- **Messages**: Internal messaging system between members
- **Resources**: Downloadable files and documents

### Key Components

#### Authentication System
- Secure password hashing using SHA-256
- Role-based access control (Admin, Member, Alumni)
- Session state management

#### Networking Features
- Member-to-member connections
- Messaging system with read receipts
- Alumni-student matching algorithm
- Profile discovery with advanced filtering

#### Portfolio Management
- Project upload and categorization
- View and download tracking
- Tag-based organization
- Analytics on project performance

#### Job Board
- Advanced filtering by type, location, experience level
- Application tracking and status updates
- Company-specific application analytics
- Salary range transparency

## <¨ UI/UX Features

### USC Branding
- Official USC colors (Cardinal Red #990000, Gold #FFC72C)
- Consistent typography and spacing
- Professional color scheme with hover effects

### Interactive Elements
- Dynamic charts and visualizations using Plotly
- Real-time metrics and analytics
- Responsive design for mobile and desktop
- Intuitive navigation with role-based menus

### Data Visualization
- Member growth trends
- Job placement analytics
- Engagement metrics
- Geographic distribution maps
- Event attendance tracking

## =È Analytics & Reporting

### Member Analytics
- Growth trends over time
- Engagement rate tracking
- Geographic distribution
- Major and specialization breakdown

### Job Market Analysis
- Placement success rates by company
- Salary range analysis
- Application-to-offer conversion rates
- Industry trend tracking

### Financial Reporting
- Revenue tracking (membership fees, events, partnerships)
- Cost per member analysis
- ROI on events and programs
- Budget planning and forecasting

## =' Customization

### Adding New Features
1. Update the mock database structure in `MockDatabase` class
2. Add new page logic in the main content area
3. Update navigation menus for appropriate roles
4. Add any required helper functions

### Styling
- Modify CSS in the `st.markdown()` section for custom styling
- Update USC branding colors in the CSS variables
- Adjust layout and spacing using Streamlit columns and containers

### Data Integration
- Replace `MockDatabase` with actual database connections
- Implement real authentication system
- Add file upload functionality for resources and portfolios
- Integrate with email services for notifications

## =€ Deployment

### Streamlit Cloud
1. Push code to GitHub repository
2. Connect to Streamlit Cloud
3. Deploy with automatic updates

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install streamlit pandas plotly numpy Pillow

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Production Considerations
- Implement proper authentication (OAuth, LDAP)
- Use real database (PostgreSQL, MongoDB)
- Add HTTPS and security headers
- Implement logging and monitoring
- Set up backup and recovery procedures

## > Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## =Ý Future Enhancements

### Planned Features
- **Real-time Chat**: WebSocket-based messaging system
- **Mobile App**: React Native companion app
- **Calendar Integration**: Google Calendar and Outlook sync
- **Payment Processing**: Stripe integration for membership fees
- **Email Automation**: Automated newsletters and notifications
- **Video Conferencing**: Integrated Zoom/Teams for virtual events
- **Document Collaboration**: Google Docs-style collaborative editing
- **Advanced Matching**: ML-based mentor-mentee matching algorithm

### Technical Improvements
- **Database Migration**: Move from mock data to production database
- **User Authentication**: Implement OAuth 2.0 with USC SSO
- **File Storage**: AWS S3 or Google Cloud Storage for portfolios
- **Caching**: Redis for improved performance
- **API Development**: REST API for mobile app integration
- **Testing Suite**: Comprehensive unit and integration tests

## =Þ Support

For questions, issues, or feature requests:
- Email: admin@usctrea.com
- GitHub Issues: [Create an issue](https://github.com/your-repo/issues)
- USC TREA Website: [usctrea.com](https://usctrea.com)

## =Ä License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with d for the USC TREA community**

*Connecting Trojans in Real Estate Since 2024*