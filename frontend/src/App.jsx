import { useState } from "react";
import Dashboard from "./components/Dashboard/Dashboard";
import { LoginForm } from "./components/LoginForm/LoginForm";

// App is the root of the application.
// It simply renders the Dashboard component upon login.
// - If no user is logged in, show LoginForm.
// - Once logged in, pass the email down to Dashboard so it can
//   display the username in the sidebar footer.
function App() {
  const [user, setUser] = useState(null); // null = logged out, { email, id, token } when logged in
  const handleLogin = (email, id, token) => setUser({ email, id, token });

  const handleLogout = ()      => setUser(null);

  if (!user) {
    return <LoginForm onLogin={handleLogin} />;
  }

  return <Dashboard user={user.email} onLogout={handleLogout} />;
}

export default App;
