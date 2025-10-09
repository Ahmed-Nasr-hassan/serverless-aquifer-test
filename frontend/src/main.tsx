import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import './index.css'
import { AuthProvider } from './contexts/AuthContext'
import RootLayout from './shell/RootLayout'
import Dashboard from './pages/Dashboard'
import Simulations from './pages/Simulations'
import ModelInputs from './pages/ModelInputs'
import WellData from './pages/WellData'
import AquiferData from './pages/AquiferData'
import OptimizationResults from './pages/OptimizationResults'
import CreateSimulation from './pages/CreateSimulation'
import CreateModelInput from './pages/CreateModelInput'
import Login from './pages/Login'

const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: 'simulations', element: <Simulations /> },
      { path: 'simulations/create', element: <CreateSimulation /> },
      { path: 'model-inputs', element: <ModelInputs /> },
      { path: 'model-inputs/create', element: <CreateModelInput /> },
      { path: 'well-data', element: <WellData /> },
      { path: 'aquifer-data', element: <AquiferData /> },
      { path: 'optimization-results', element: <OptimizationResults /> },
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
