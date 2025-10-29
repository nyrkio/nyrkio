# Frontend Development

The Nyrkiö frontend is a React application built with Vite.

## Project Structure

```
frontend/
├── src/
│   ├── components/      # React components
│   ├── pages/           # Page components
│   ├── hooks/           # Custom hooks
│   ├── utils/           # Utility functions
│   ├── api/             # API client
│   ├── context/         # React context
│   └── App.jsx          # Main app component
├── public/              # Static assets
├── vite.config.js       # Production config
└── vite.config.test.js  # Local dev config
```

## Development Setup

```bash
cd frontend
npm install

# Start with local backend
python3 etc/nyrkio_frontend.py start

# Or with npm directly
npm run dev -- --config vite.config.test.js
```

## Creating Components

### Functional Component

```jsx
import React from 'react';

export function MyComponent({ title, value }) {
  return (
    <div className="my-component">
      <h2>{title}</h2>
      <p>{value}</p>
    </div>
  );
}
```

### Component with Hooks

```jsx
import React, { useState, useEffect } from 'react';

export function Counter() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    document.title = `Count: ${count}`;
  }, [count]);

  return (
    <button onClick={() => setCount(count + 1)}>
      Count: {count}
    </button>
  );
}
```

## API Integration

### Using TanStack Query

```jsx
import { useQuery } from '@tanstack/react-query';

function TestResults({ testName }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['test', testName],
    queryFn: () => fetch(`/api/v0/result/${testName}`).then(r => r.json())
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return <div>{JSON.stringify(data)}</div>;
}
```

### Mutations

```jsx
import { useMutation, useQueryClient } from '@tanstack/react-query';

function SubmitResult({ testName }) {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: (newResult) => {
      return fetch(`/api/v0/result/${testName}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newResult)
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['test', testName] });
    }
  });

  return (
    <button onClick={() => mutation.mutate({ value: 123 })}>
      Submit
    </button>
  );
}
```

## Routing

### React Router Setup

```jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/tests/:testName" element={<TestDetails />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </BrowserRouter>
  );
}
```

### Navigation

```jsx
import { Link, useNavigate } from 'react-router-dom';

function Navigation() {
  const navigate = useNavigate();

  return (
    <nav>
      <Link to="/">Home</Link>
      <button onClick={() => navigate('/settings')}>
        Settings
      </button>
    </nav>
  );
}
```

## State Management

### Context API

```jsx
import React, { createContext, useContext, useState } from 'react';

const UserContext = createContext();

export function UserProvider({ children }) {
  const [user, setUser] = useState(null);

  return (
    <UserContext.Provider value={{ user, setUser }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUser must be used within UserProvider');
  }
  return context;
}
```

## Visualization with Recharts

```jsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

function PerformanceChart({ data }) {
  return (
    <LineChart width={600} height={300} data={data}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="timestamp" />
      <YAxis />
      <Tooltip />
      <Line type="monotone" dataKey="value" stroke="#8884d8" />
    </LineChart>
  );
}
```

## Styling

### CSS Modules

```jsx
import styles from './MyComponent.module.css';

function MyComponent() {
  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Hello</h1>
    </div>
  );
}
```

### Tailwind CSS

```jsx
function MyComponent() {
  return (
    <div className="flex items-center justify-between p-4 bg-gray-100">
      <h1 className="text-2xl font-bold">Hello</h1>
    </div>
  );
}
```

## Configuration

### Vite Config

**Local Development** (`vite.config.test.js`):
```javascript
export default defineConfig({
  server: {
    proxy: {
      '/api': 'http://localhost:8001'
    }
  }
});
```

**Production** (`vite.config.js`):
```javascript
export default defineConfig({
  server: {
    proxy: {
      '/api': 'https://nyrk.io'
    }
  }
});
```

## Build and Deploy

```bash
# Development build
npm run build

# Preview production build
npm run preview

# Run tests
npm run test
```

## Common Patterns

### Loading States

```jsx
function DataLoader() {
  const { data, isLoading } = useQuery(['data'], fetchData);

  if (isLoading) {
    return <Spinner />;
  }

  return <DataDisplay data={data} />;
}
```

### Error Boundaries

```jsx
import { ErrorBoundary } from 'react-error-boundary';

function ErrorFallback({ error }) {
  return (
    <div role="alert">
      <p>Something went wrong:</p>
      <pre>{error.message}</pre>
    </div>
  );
}

function App() {
  return (
    <ErrorBoundary FallbackComponent={ErrorFallback}>
      <MyApp />
    </ErrorBoundary>
  );
}
```
