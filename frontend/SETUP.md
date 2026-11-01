# Getting Started with Alumni ML Frontend

## Quick Start (5 minutes)

### 1. Prerequisites
- Node.js 16+ installed
- npm or yarn package manager
- Backend running on http://localhost:5000

### 2. Installation

```bash
cd frontend
npm install
```

### 3. Configuration

Create a `.env` file:
```bash
cp .env.example .env
```

Edit `.env` and set your backend URL:
```
REACT_APP_API_URL=http://localhost:5000
```

### 4. Start Development Server

```bash
npm start
```

The application will open automatically at http://localhost:3000

## Demo Credentials

```
Email: demo@alumni.edu
Password: demo123
```

## Available Scripts

### `npm start`
Runs the app in development mode with hot reload.

### `npm run build`
Builds the app for production.

### `npm test`
Launches the test runner.

### `npm run eject`
⚠️ One-way operation to expose webpack config (not recommended).

## Project Features

### 📊 Dashboard
- Real-time metrics and statistics
- Alumni engagement trends
- Donation visualization
- Top performers tracking

### 👥 Alumni Management
- Search and view alumni profiles
- Track engagement history
- View donation records
- ML prediction scores

### 📝 Record Entry
- Log engagement events (attendance, newsletter, login, etc.)
- Record donations with fund type selection
- Support for multiple payment methods
- Timestamp tracking

### 📈 Forecasting
- Segment-based donation forecasting
- Predicted donor counts and amounts
- Model confidence scores
- Actionable recommendations
- Trend visualization

### 🤖 AI Insights
- Natural language Q&A interface
- GenAI-powered analysis
- Suggested analysis questions
- Confidence metrics
- Conversation history

## API Integration

The frontend communicates with the backend through REST API endpoints:

```
POST   /alumni/engagement      - Record engagement
POST   /alumni/donation        - Record donation  
GET    /alumni/{alumni_id}     - Get alumni profile
POST   /alumni/forecast        - Generate forecast
GET    /alumni/insights        - Get AI insights
```

All API calls automatically include authentication headers and handle token refresh.

## Customization

### Changing Colors

Edit the CSS files to customize colors. Main color definitions are in component CSS files.

### Adding New Pages

1. Create a new component in `src/pages/`
2. Add route in `App.js`
3. Add navigation link in `Navigation.js`

### Modifying Components

Components are in `src/components/` and can be customized for styling and functionality.

## Deployment

### Docker Deployment

```bash
# Build image
docker build -t alumni-frontend .

# Run container
docker run -p 3000:3000 -e REACT_APP_API_URL=http://backend:5000 alumni-frontend
```

### Docker Compose (with backend)

```bash
docker-compose up
```

### Static Hosting (Netlify, Vercel, etc.)

1. Build the app:
   ```bash
   npm run build
   ```

2. Deploy the `build/` folder to your hosting provider

3. Set environment variables in hosting platform:
   ```
   REACT_APP_API_URL=https://your-backend-api.com
   ```

## Troubleshooting

### Issue: API Connection Failed
**Solution:**
- Check backend is running: `curl http://localhost:5000/health`
- Verify REACT_APP_API_URL in .env
- Check browser console for errors (F12)

### Issue: Port 3000 Already in Use
**Solution:**
```bash
# Use different port
PORT=3001 npm start

# Or kill process on port 3000
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:3000 | xargs kill -9
```

### Issue: Dependencies Not Installing
**Solution:**
```bash
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### Issue: Blank Page After Login
**Solution:**
- Open browser DevTools (F12)
- Check Console tab for errors
- Verify token is stored in localStorage
- Check if backend is responding to API calls

## Browser DevTools Tips

### Redux DevTools (if added)
Monitor state changes and actions in detail

### Network Tab
- Monitor API calls
- Check response status and headers
- View request/response payload

### Console
- Check for errors and warnings
- Run custom JavaScript to debug

## Performance Tips

- Use React DevTools browser extension
- Profile components with React Profiler
- Check bundle size: `npm run build`
- Analyze with: `source-map-explorer 'build/static/js/*.js'`

## Next Steps

1. ✅ Install dependencies
2. ✅ Configure API URL
3. ✅ Start development server
4. ✅ Log in with demo credentials
5. ✅ Explore the dashboard
6. ✅ Test recording engagement
7. ✅ Test recording donation
8. ✅ Generate forecasts
9. ✅ Ask AI insights

## Support & Feedback

For issues, feature requests, or questions:
1. Check this README
2. Check the browser console for errors
3. Review API responses in Network tab
4. Contact the development team

## Resources

- [React Documentation](https://react.dev)
- [React Router Guide](https://reactrouter.com)
- [Axios Documentation](https://axios-http.com)
- [Recharts Examples](https://recharts.org)

## License

MIT License - See LICENSE file for details
