"""
Component Style Guide & Development Patterns
Alumni ML Pipeline Frontend
"""

# Navigation Component

Used for: Main app navigation bar
Location: src/components/Navigation.js

## Features:
- Sticky top navigation
- Mobile hamburger menu
- User info display
- Logout functionality
- Active route indication

## Usage:
```jsx
<Navigation user={user} onLogout={handleLogout} />
```

## Props:
- `user` (object): Current user data
- `onLogout` (function): Logout callback

---

# Card Component

Used for: Content containers with optional title
Location: src/components/Card.js

## Features:
- Header with title (optional)
- Content area
- Flexible styling

## Usage:
```jsx
<Card title="My Title" className="custom-class">
  <p>Content goes here</p>
</Card>
```

## Props:
- `title` (string): Optional card title
- `className` (string): Additional CSS class
- `children` (ReactNode): Card content

---

# Button Component

Used for: All interactive buttons
Location: src/components/Button.js

## Features:
- Multiple variants (primary, secondary, success, danger, warning)
- Multiple sizes (sm, md, lg)
- Loading state
- Disabled state

## Usage:
```jsx
<Button
  variant="primary"
  size="lg"
  loading={isLoading}
  onClick={handleClick}
  disabled={isDisabled}
>
  Click Me
</Button>
```

## Props:
- `variant` (string): primary|secondary|success|danger|warning
- `size` (string): sm|md|lg
- `loading` (boolean): Show loading state
- `disabled` (boolean): Disable button
- `type` (string): button|submit|reset
- `onClick` (function): Click handler
- `className` (string): Additional CSS classes

## Variants:
- **primary**: Blue - primary actions
- **secondary**: Gray - secondary actions
- **success**: Green - positive/confirmation actions
- **danger**: Red - destructive actions
- **warning**: Orange - caution/warning actions

---

# Alert Component

Used for: Notifications and alerts
Location: src/components/Alert.js

## Features:
- Multiple alert types
- Dismissible
- Auto-close animation

## Usage:
```jsx
<Alert
  type="success"
  message="Operation successful!"
  onClose={() => setAlert(null)}
/>
```

## Props:
- `type` (string): info|success|warning|error
- `message` (string): Alert message
- `onClose` (function, optional): Dismiss callback

## Types:
- **info**: Blue - informational messages
- **success**: Green - successful operations
- **warning**: Orange - warning messages
- **error**: Red - error messages

---

# Loading Component

Used for: Loading spinners and messages
Location: src/components/Loading.js

## Features:
- Animated spinner
- Custom message
- Centered layout

## Usage:
```jsx
<Loading message="Loading data..." />
```

## Props:
- `message` (string, optional): Loading message

---

# Form Patterns

## Form Input Group
```jsx
<div className="form-group">
  <label htmlFor="name">Field Label</label>
  <input
    id="name"
    type="text"
    name="name"
    value={formData.name}
    onChange={handleChange}
    placeholder="Placeholder text"
  />
</div>
```

## Form Submission
```jsx
const handleSubmit = async (e) => {
  e.preventDefault();
  setLoading(true);
  
  try {
    // API call
    const response = await alumniAPI.recordEngagement(formData);
    setSuccess(true);
    setFormData({...}); // Reset form
  } catch (error) {
    setError(error.message);
  } finally {
    setLoading(false);
  }
};
```

## Form Validation
```jsx
const handleChange = (e) => {
  const { name, value } = e.target;
  
  // Validate
  if (name === 'amount' && parseFloat(value) < 0) {
    setError('Amount must be positive');
    return;
  }
  
  setFormData(prev => ({ ...prev, [name]: value }));
};
```

---

# API Integration Patterns

## Making API Calls
```jsx
import { alumniAPI } from '../services/api';

// In component
useEffect(() => {
  const fetchData = async () => {
    try {
      const response = await alumniAPI.getAlumni(alumniId);
      setData(response.data);
    } catch (error) {
      setError(error.response?.data?.error || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };
  
  fetchData();
}, [alumniId]);
```

## Error Handling
```jsx
try {
  const response = await alumniAPI.recordDonation(data);
  // Handle success
} catch (error) {
  if (error.response?.status === 401) {
    // Handle auth error
    navigate('/login');
  } else if (error.response?.status === 400) {
    // Handle validation error
    setError(error.response.data.details);
  } else {
    // Handle generic error
    setError('An error occurred. Please try again.');
  }
}
```

---

# State Management Patterns

## Using useState for Form Data
```jsx
const [formData, setFormData] = useState({
  alumniId: '',
  amount: '',
  fundType: 'general',
  date: new Date().toISOString().split('T')[0],
});

const handleChange = (e) => {
  const { name, value } = e.target;
  setFormData(prev => ({
    ...prev,
    [name]: value,
  }));
};
```

## Using useState for UI State
```jsx
const [loading, setLoading] = useState(false);
const [error, setError] = useState('');
const [success, setSuccess] = useState(false);
```

## Using useEffect for Side Effects
```jsx
useEffect(() => {
  // Fetch data
  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await api.getData();
      setData(response.data);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };
  
  fetchData();
}, [dependencies]);
```

---

# Routing Patterns

## Protected Routes
```jsx
<Route
  path="/dashboard"
  element={
    isAuthenticated ? (
      <Dashboard user={user} />
    ) : (
      <Navigate to="/login" replace />
    )
  }
/>
```

## Navigation
```jsx
import { useNavigate } from 'react-router-dom';

const navigate = useNavigate();
navigate('/path');
```

## URL Parameters
```jsx
import { useParams } from 'react-router-dom';

const { alumniId } = useParams();
```

---

# CSS Patterns

## Responsive Grid
```css
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}
```

## Flexbox Layout
```css
.flex-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}
```

## Cards with Shadow
```css
.card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
}
```

## Transitions
```css
.button {
  transition: all 0.3s ease;
}

.button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
```

## Gradient Background
```css
.gradient {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
```

---

# Common Component Implementations

## Data Table
```jsx
<table className="data-table">
  <thead>
    <tr>
      <th>Column 1</th>
      <th>Column 2</th>
    </tr>
  </thead>
  <tbody>
    {data.map(row => (
      <tr key={row.id}>
        <td>{row.col1}</td>
        <td>{row.col2}</td>
      </tr>
    ))}
  </tbody>
</table>
```

## Modal/Dialog
```jsx
{isOpen && (
  <div className="modal-overlay" onClick={onClose}>
    <div className="modal" onClick={e => e.stopPropagation()}>
      <h2>Modal Title</h2>
      <p>Modal content</p>
      <Button onClick={onClose}>Close</Button>
    </div>
  </div>
)}
```

## Dropdown Menu
```jsx
<select 
  name="fieldName"
  value={value}
  onChange={handleChange}
>
  {options.map(option => (
    <option key={option.value} value={option.value}>
      {option.label}
    </option>
  ))}
</select>
```

## Search/Filter
```jsx
const [searchTerm, setSearchTerm] = useState('');

const filtered = data.filter(item =>
  item.name.toLowerCase().includes(searchTerm.toLowerCase())
);
```

---

# Testing Code Patterns

## Component Test Example
```jsx
import { render, screen } from '@testing-library/react';
import MyComponent from './MyComponent';

test('renders component', () => {
  render(<MyComponent />);
  expect(screen.getByText('text')).toBeInTheDocument();
});
```

## API Mock Pattern
```jsx
jest.mock('../services/api', () => ({
  alumniAPI: {
    getAlumni: jest.fn(() => 
      Promise.resolve({ data: { id: 1, name: 'John' } })
    ),
  },
}));
```

---

# Performance Optimization Patterns

## Memo for Component
```jsx
import { memo } from 'react';

const MyComponent = memo(({ prop }) => {
  return <div>{prop}</div>;
});
```

## useCallback for Functions
```jsx
import { useCallback } from 'react';

const handleClick = useCallback(() => {
  // Function to optimize
}, [dependencies]);
```

## Lazy Load Components
```jsx
import { lazy, Suspense } from 'react';

const Dashboard = lazy(() => import('./Dashboard'));

<Suspense fallback={<Loading />}>
  <Dashboard />
</Suspense>
```

---

# Accessibility Patterns

## Form Labels
```jsx
<label htmlFor="input-id">Label Text</label>
<input id="input-id" type="text" />
```

## Alt Text for Images
```jsx
<img src="image.jpg" alt="Descriptive text" />
```

## ARIA Attributes
```jsx
<button aria-label="Close menu">×</button>
<div role="alert">{message}</div>
```

---

# Code Organization

## File Structure
```
src/
├── components/       # Reusable components
├── pages/           # Page-level components  
├── services/        # API and utility services
├── assets/          # Images, fonts
├── styles/          # Global styles
├── hooks/           # Custom React hooks
└── utils/           # Helper functions
```

## Import Order
```jsx
// 1. React and libraries
import React, { useState } from 'react';
import { useParams } from 'react-router-dom';

// 2. Components
import Card from '../components/Card';
import Button from '../components/Button';

// 3. Utilities and services
import { alumniAPI } from '../services/api';
import { formatCurrency } from '../utils/format';

// 4. Styles
import './MyComponent.css';
```

---

# Best Practices

✅ **DO:**
- Use functional components with hooks
- Separate concerns (logic, UI, styles)
- Handle all error cases
- Use meaningful variable names
- Add loading and error states
- Validate form inputs
- Use CSS classes instead of inline styles
- Clean up subscriptions in useEffect

❌ **DON'T:**
- Use state for static data
- Ignore error cases
- Create too many props (consider composition)
- Use var (use const/let)
- Mutate state directly
- Add unnecessary re-renders
- Leave console.log in production code
- Ignore accessibility requirements
