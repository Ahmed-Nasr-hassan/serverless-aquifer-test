import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import './index.css'
import { AuthProvider } from './contexts/AuthContext'
import RootLayout from './shell/RootLayout'
import Dashboard from './pages/Dashboard'
import Simulations from './pages/Simulations'
import ModelInputs from './pages/ModelInputs'
import Login from './pages/Login'

const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: 'simulations', element: <Simulations /> },
      { path: 'model-inputs', element: <ModelInputs /> },
    ],
  },
  { path: '/login', element: <Login /> },
])

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AuthProvider>
      <RouterProvider router={router} />
    </AuthProvider>
  </StrictMode>,
)
