# Frontend Project Structure

```
frontend/
│
├── public/
│   ├── index.html              # HTML entry point
│   └── favicon.ico
│
├── src/
│   ├── components/             # Reusable UI components
│   │   ├── Navigation.js       # Main navigation bar
│   │   ├── Navigation.css
│   │   ├── Card.js             # Card container component
│   │   ├── Card.css
│   │   ├── Button.js           # Button component
│   │   ├── Button.css
│   │   ├── Alert.js            # Alert/notification component
│   │   ├── Alert.css
│   │   ├── Loading.js          # Loading spinner
│   │   └── Loading.css
│   │
│   ├── pages/                  # Page-level components
│   │   ├── Login.js            # Login/authentication page
│   │   ├── Login.css
│   │   ├── Dashboard.js        # Main dashboard
│   │   ├── Dashboard.css
│   │   ├── AlumniProfile.js    # Alumni detail page
│   │   ├── AlumniProfile.css
│   │   ├── RecordEngagement.js # Record engagement form
│   │   ├── RecordEngagement.css
│   │   ├── RecordDonation.js   # Record donation form
│   │   ├── RecordDonation.css
│   │   ├── Forecast.js         # Donation forecasting page
│   │   ├── Forecast.css
│   │   ├── Insights.js         # AI insights page
│   │   └── Insights.css
│   │
│   ├── services/               # API and services
│   │   └── api.js              # Axios API client and endpoints
│   │
│   ├── utils/                  # Utility functions
│   │   ├── format.js           # Formatting utilities
│   │   ├── validation.js       # Form validation
│   │   └── constants.js        # App constants
│   │
│   ├── App.js                  # Main app component
│   ├── App.css                 # App-level styles
│   ├── index.js                # React entry point
│   └── index.css               # Global styles
│
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── Dockerfile                  # Docker build configuration
├── docker-compose.yml          # Docker compose setup
├── package.json                # Dependencies and scripts
├── README.md                   # Project README
├── SETUP.md                    # Setup instructions
├── API_DOCUMENTATION.md        # API reference
├── DEVELOPER_GUIDE.md          # Component guide
├── setup.sh                    # Unix setup script
└── setup.bat                   # Windows setup script
```

## Component Hierarchy

```
App
├── Navigation
├── Routes
│   ├── Login
│   ├── Dashboard
│   │   ├── Card (metrics)
│   │   ├── LineChart
│   │   ├── PieChart
│   │   ├── Table
│   │   └── Badge
│   ├── AlumniProfile
│   │   ├── Card (profile header)
│   │   ├── Card (stats)
│   │   ├── Card (predictions)
│   │   └── Timeline
│   ├── RecordEngagement
│   │   ├── Card (form)
│   │   ├── Button
│   │   └── Alert
│   ├── RecordDonation
│   │   ├── Card (form)
│   │   ├── Button
│   │   └── Alert
│   ├── Forecast
│   │   ├── Card (parameters)
│   │   ├── Button
│   │   ├── BarChart
│   │   └── Table
│   └── Insights
│       ├── Card (question input)
│       ├── Button
│       └── Message (conversation)
```

## Data Flow

```
User Input → Component State → API Call → Response → Update UI
```

## Authentication Flow

```
1. User logs in on Login page
2. Credentials sent to /auth/login
3. Backend returns JWT token
4. Token stored in localStorage
5. Token added to all API requests
6. Protected routes check authentication
7. 401 responses redirect to login
8. Logout clears token and redirects
```

## State Management

Components manage their own state using `useState`. For complex state sharing, consider adding Redux/Context API.

### Current Pattern:
- Local component state with `useState`
- Props drilling for shared data
- API calls in `useEffect`

### Suggested Improvements:
- Use React Context for auth state
- Consider Redux for complex state
- Implement state persistence

## Styling Architecture

### CSS Organization:
- Global styles in `index.css`
- Component-specific styles in `ComponentName.css`
- Utility classes for common patterns
- CSS variables for colors and spacing

### Color System:
```css
--primary: #3498db      (Blue)
--success: #27ae60      (Green)
--warning: #f39c12      (Orange)
--danger: #e74c3c       (Red)
--gray: #7f8c8d         (Gray)
--dark: #2c3e50         (Dark)
--light: #f5f5f5        (Light)
```

## Performance Considerations

1. **Code Splitting**: Consider lazy loading pages
2. **Memoization**: Use React.memo for expensive components
3. **API Calls**: Implement request caching
4. **Bundle Size**: Monitor with `npm run build`
5. **Images**: Optimize before using

## Security Considerations

1. **Token Handling**: Stored securely in localStorage
2. **CORS**: Handled by backend
3. **Input Validation**: Validate on client and server
4. **XSS Protection**: React escapes by default
5. **HTTPS**: Use in production only

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Dependencies Overview

| Package | Purpose |
|---------|---------|
| react | UI library |
| react-router-dom | Client routing |
| axios | HTTP client |
| recharts | Data visualization |
| lucide-react | Icon library |
| classnames | Conditional CSS |

## Environment Variables

```
REACT_APP_API_URL    - Backend API URL
REACT_APP_API_KEY    - API key (if needed)
REACT_APP_ENV        - Environment (dev/prod)
```

## Development Workflow

1. Create new branch
2. Make changes
3. Test locally
4. Commit with clear messages
5. Push and create PR
6. Code review
7. Merge to main

## Deployment Checklist

- [ ] All tests passing
- [ ] No console errors/warnings
- [ ] Environment variables configured
- [ ] API URL points to production
- [ ] Build succeeds
- [ ] Bundle size acceptable
- [ ] Performance tested
- [ ] Security audit passed
