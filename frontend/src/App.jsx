import { useState } from "react";
import Dashboard from "./components/Dashboard/Dashboard";
import { LoginForm } from "./components/LoginForm/LoginForm";

// App is the root of the application
// It simply renders the Dashboard component upon login
// - If no user is logged in, show LoginForm
// - Once logged in, pass the user to Dashboard
// - State is seeded from localStorage so the session survives page refreshes.
function App() {
  const [user, setUser] = useState(() => {
    const token = localStorage.getItem("token");
    const id    = localStorage.getItem("userId");
    const email = localStorage.getItem("userEmail");
    return token ? { email, id: parseInt(id), token } : null;
  }); 

  const handleLogin = (email, id, token) => {
    localStorage.setItem("token",     token);
    localStorage.setItem("userId",    id);
    localStorage.setItem("userEmail", email);
    setUser({ email, id, token });
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("userId");
    localStorage.removeItem("userEmail");
    setUser(null);
  };

  if (!user) {
    return <LoginForm onLogin={handleLogin} />;
  }

  return (
    <Dashboard
      user={user.email}
      userId={user.id}
      token={user.token}
      onLogout={handleLogout}
  />
  );
}

export default App;
