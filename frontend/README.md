# Alumni ML Pipeline - React Frontend

A modern React.js frontend for the Alumni ML Pipeline, enabling donation and engagement prediction for universities.

## Features

✨ **Dashboard**
- View key metrics and alumni statistics
- Engagement trends visualization
- Top donors analysis
- Donation amount tracking

👥 **Alumni Management**
- View detailed alumni profiles
- Track donation history
- Monitor engagement activities
- ML-powered prediction scores

📝 **Record Entry**
- Record new engagement events (attendance, newsletter, etc.)
- Log donations with multiple fund types
- Support for various payment methods
- Audit trail for all activities

📊 **Forecasting**
- ML-powered donation forecasting by segment
- Predict donor behavior and amounts
- Segment-specific insights
- Actionable recommendations

🧠 **AI Insights**
- GenAI-powered Q&A about alumni data
- Natural language insights
- Suggested analysis questions
- Confidence scores on predictions

## Tech Stack

- **React 18** - UI framework
- **React Router v6** - Client-side routing
- **Axios** - HTTP client
- **Recharts** - Data visualization
- **Lucide React** - Icon library
- **CSS3** - Styling

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Navigation.js        # Main navigation bar
│   │   ├── Card.js              # Reusable card component
│   │   ├── Button.js            # Reusable button component
│   │   ├── Alert.js             # Alert/notification component
│   │   └── Loading.js           # Loading spinner
│   ├── pages/
│   │   ├── Login.js             # Authentication page
│   │   ├── Dashboard.js         # Main dashboard
│   │   ├── AlumniProfile.js     # Alumni detail view
│   │   ├── RecordEngagement.js  # Record engagement form
│   │   ├── RecordDonation.js    # Record donation form
│   │   ├── Forecast.js          # Donation forecasting
│   │   └── Insights.js          # AI insights page
│   ├── services/
│   │   └── api.js               # API client and endpoints
│   ├── App.js                   # Main app component
│   ├── index.js                 # React entry point
│   └── styles/                  # Global styles
├── package.json
└── .env.example
```

## Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
```

4. Update `.env` with your backend API URL:
```
REACT_APP_API_URL=http://localhost:5000
```

## Running the Application

### Development Mode
```bash
npm start
```
The app will open at `http://localhost:3000`

### Build for Production
```bash
npm run build
```

### Run Tests
```bash
npm test
```

## Authentication

The application includes a demo login page. Default credentials:
- **Email**: demo@alumni.edu
- **Password**: demo123

For production, integrate with your actual authentication backend.

## API Integration

The application integrates with the alumni ML pipeline backend. Key endpoints:

### Alumni Endpoints
- `GET /alumni/:alumniId` - Get alumni profile
- `POST /alumni/engagement` - Record engagement event
- `POST /alumni/donation` - Record donation
- `POST /alumni/forecast` - Generate donation forecast
- `GET /alumni/insights` - Get GenAI insights

### Authentication
- Tokens are stored in localStorage
- API calls automatically include authorization headers
- 401 responses redirect to login page

## Component Usage Examples

### Card Component
```jsx
<Card title="My Card Title">
  <p>Card content goes here</p>
</Card>
```

### Button Component
```jsx
<Button
  variant="primary"
  size="lg"
  loading={isLoading}
  onClick={handleClick}
>
  Click Me
</Button>
```

### Alert Component
```jsx
<Alert
  type="success"
  message="Operation successful!"
  onClose={() => setAlert(null)}
/>
```

## Styling

The application uses:
- **CSS Modules** for component-specific styles
- **CSS Grid & Flexbox** for layouts
- **CSS Variables** for colors and spacing
- **Responsive design** for mobile compatibility

### Color Scheme
- Primary: #3498db (Blue)
- Success: #27ae60 (Green)
- Warning: #f39c12 (Orange)
- Danger: #e74c3c (Red)
- Background: #f5f5f5 (Light Gray)
- Text: #2c3e50 (Dark Gray)

## Responsive Design

The application is fully responsive and tested on:
- Desktop (1200px+)
- Tablet (768px - 1199px)
- Mobile (< 768px)

## Environment Variables

Create a `.env` file with:
```
REACT_APP_API_URL=http://localhost:5000
REACT_APP_API_KEY=your_api_key
REACT_APP_ENV=development
```

## Performance Optimization

- Code splitting with React.lazy()
- Image optimization
- Memoized components
- Efficient re-renders
- Cached API responses

## Security

- XSS protection via React's built-in escaping
- CSRF token handling
- Secure token storage
- HTTPS in production
- Input validation on all forms

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Troubleshooting

### API Connection Issues
- Ensure backend is running (usually on http://localhost:5000)
- Check REACT_APP_API_URL in .env matches your backend
- Check browser console for CORS errors

### Login Issues
- Clear localStorage: `localStorage.clear()`
- Check network tab for API response
- Verify credentials are correct

### Build Issues
- Delete node_modules: `rm -rf node_modules`
- Clear npm cache: `npm cache clean --force`
- Reinstall: `npm install`

## Contributing

1. Create a new branch for features
2. Follow existing code style
3. Test changes thoroughly
4. Create pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and feature requests, please contact the development team.
