import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Navbar from "./components/Navbar";
import { ToastContainer } from "./components/Toast";
import Login from "./pages/Login";
import UploadCV from "./pages/UploadCV";
import Matches from "./pages/Matches";
import JobDetail from "./pages/JobDetail";
import Applications from "./pages/Applications";
import Settings from "./pages/Settings";

function RequireAuth({ children }) {
  const token = localStorage.getItem("token");
  if (!token) return <Navigate to="/login" replace />;
  return children;
}

function AuthLayout({ children }) {
  return (
    <>
      <Navbar />
      <main>{children}</main>
    </>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/upload"
          element={
            <RequireAuth>
              <AuthLayout><UploadCV /></AuthLayout>
            </RequireAuth>
          }
        />
        <Route
          path="/matches"
          element={
            <RequireAuth>
              <AuthLayout><Matches /></AuthLayout>
            </RequireAuth>
          }
        />
        <Route
          path="/jobs/:jobId"
          element={
            <RequireAuth>
              <AuthLayout><JobDetail /></AuthLayout>
            </RequireAuth>
          }
        />
        <Route
          path="/applications"
          element={
            <RequireAuth>
              <AuthLayout><Applications /></AuthLayout>
            </RequireAuth>
          }
        />
        <Route
          path="/settings"
          element={
            <RequireAuth>
              <AuthLayout><Settings /></AuthLayout>
            </RequireAuth>
          }
        />
        <Route path="*" element={<Navigate to="/matches" replace />} />
      </Routes>
      <ToastContainer />
    </BrowserRouter>
  );
}
