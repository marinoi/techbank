import './App.css'
import { Route, Routes } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import Footer from './components/Footer'
import HomePage from './pages/HomePage'
import NavBar from './components/NavBar'
import SigninPage from './pages/SigninPage'
import { RequiredRoleRouting, Roles } from './contexts/RoleContext'
import WalletPage from './pages/WalletPage'
import AdminDashboard from './pages/AdminDashboard'
import NotificationPage from './pages/NotificationPage'
import CardPage from './pages/CardsPage'
import AdminApiPage from './pages/AdminApiPage'


function App() {
  return (
    <>
      <div className="flex flex-col min-h-screen">
        <NavBar />
        <main className="flex-grow">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signin" element={<SigninPage/>} />

            <Route path="/wallet"
              element={
                <RequiredRoleRouting allowedRoles={[Roles.USER]}>
                  <WalletPage />
                </RequiredRoleRouting>
              }
            />

            
            <Route path="/cards"
              element={
                <RequiredRoleRouting allowedRoles={[Roles.USER]}>
                  <CardPage />
                </RequiredRoleRouting>
              }
            />

            <Route path="/notification"
              element={
                <RequiredRoleRouting allowedRoles={[Roles.USER]}>
                  <NotificationPage />
                </RequiredRoleRouting>
              }
            />

            <Route path="/dashboard"
              element={
                <RequiredRoleRouting allowedRoles={[Roles.ADMIN]}>
                  <AdminDashboard />
                </RequiredRoleRouting>
              }
            />
            <Route path="/stress-test"
              element={
                <RequiredRoleRouting allowedRoles={[Roles.ADMIN]}>
                  <AdminApiPage />
                </RequiredRoleRouting>
              }
            />
          </Routes>
        </main>
        <Footer />
      </div>
    </>
  );
}

export default App
