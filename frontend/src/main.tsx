import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import './index.css'
import { AuthProvider } from './contexts/AuthContext'
import { ThemeProvider } from './contexts/ThemeContext'
import RootLayout from './shell/RootLayout'
import Dashboard from './pages/Dashboard'
import Simulations from './pages/Simulations'
import ModelInputs from './pages/ModelInputs'
import WellData from './pages/WellData'
import AquiferData from './pages/AquiferData'
import OptimizationResults from './pages/OptimizationResults'
import CreateSimulation from './pages/CreateSimulation'
import CreateModelInput from './pages/CreateModelInput'
import EditSimulation from './pages/EditSimulation'
import EditModelInput from './pages/EditModelInput'
import Login from './pages/Login'

const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: 'simulations', element: <Simulations /> },
      { path: 'simulations/create', element: <CreateSimulation /> },
      { path: 'simulations/edit/:id', element: <EditSimulation /> },
      { path: 'model-inputs', element: <ModelInputs /> },
      { path: 'model-inputs/create', element: <CreateModelInput /> },
      { path: 'model-inputs/edit/:id', element: <EditModelInput /> },
      { path: 'well-data', element: <WellData /> },
      { path: 'aquifer-data', element: <AquiferData /> },
      { path: 'optimization-results', element: <OptimizationResults /> },
    ],
  },
  { path: '/login', element: <Login /> },
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
