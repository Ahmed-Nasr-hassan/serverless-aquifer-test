import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import './index.css'
import { AuthProvider } from './contexts/AuthContext'
import { ThemeProvider } from './contexts/ThemeContext'
import RootLayout from './shell/RootLayout'
import Dashboard from './pages/Dashboard'
import Models from './pages/Models'
import ModelDetail from './pages/ModelDetail'
import EditModel from './pages/EditModel'
import CreateModel from './pages/CreateModel'
import Simulations from './pages/Simulations'
import CreateSimulation from './pages/CreateSimulation'
import EditSimulation from './pages/EditSimulation'
import Login from './pages/Login'
import SignUp from './pages/SignUp'

const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: 'models', element: <Models /> },
      { path: 'models/:id', element: <ModelDetail /> },
      { path: 'models/:id/edit', element: <EditModel /> },
      { path: 'models/create', element: <CreateModel /> },
              { path: 'simulations', element: <Simulations /> },
              { path: 'simulations/create', element: <CreateSimulation /> },
              { path: 'simulations/edit/:id', element: <EditSimulation /> },
    ],
  },
          { path: '/login', element: <Login /> },
          { path: '/signup', element: <SignUp /> },
])

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ThemeProvider>
      <AuthProvider>
        <RouterProvider router={router} />
      </AuthProvider>
    </ThemeProvider>
  </StrictMode>,
)
