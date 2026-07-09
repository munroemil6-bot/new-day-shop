import React, { useEffect, useState } from 'react';
import { Routes, Route, NavLink, useNavigate } from 'react-router-dom';
import './App.css';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

function ItemCard({ item }) {
  return (
    <div className="card">
      <h3>{item.name}</h3>
      <p>{item.description}</p>
      <p><strong>Price:</strong> Ksh {item.price.toFixed(2)}</p>
      <p><strong>Stock:</strong> {item.stock}</p>
    </div>
  );
}

function Home({ user }) {
  return (
    <div className="hero-card">
      <div>
        <p className="eyebrow">Fresh everyday essentials</p>
        <h2>Welcome to the Kenyan Shop</h2>
        {user ? <p>You are signed in as {user.username}.</p> : <p>Use the menu to browse products, sign up, or log in.</p>}
      </div>
      <div className="hero-highlight">
        <h3>Popular picks</h3>
        <ul>
          <li>Maize Flour</li>
          <li>Mandazi Pack</li>
          <li>Chai Tea</li>
        </ul>
      </div>
    </div>
  );
}

function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (event) => {
    event.preventDefault();
    fetch(`${API_BASE}/api/auth/login`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.error) {
          setMessage(data.error);
        } else {
          setMessage(`Logged in as ${data.username}`);
          onLogin(data);
          navigate('/shop');
        }
      })
      .catch(() => setMessage('Login failed.'));
  };

  return (
    <div className="panel">
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>
            Username or Email<br />
            <input value={username} onChange={(e) => setUsername(e.target.value)} />
          </label>
        </div>
        <div>
          <label>
            Password<br />
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          </label>
        </div>
        <button type="submit" className="button primary">Log in</button>
      </form>
      <p className="message">{message}</p>
    </div>
  );
}

function Signup() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');

  const handleSubmit = (event) => {
    event.preventDefault();
    fetch(`${API_BASE}/api/auth/signup`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.error) {
          setMessage(data.error);
        } else {
          setMessage('Account created. You can now log in.');
        }
      })
      .catch(() => setMessage('Signup failed.'));
  };

  return (
    <div className="panel">
      <h2>Signup</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>
            Username<br />
            <input value={username} onChange={(e) => setUsername(e.target.value)} />
          </label>
        </div>
        <div>
          <label>
            Email<br />
            <input value={email} onChange={(e) => setEmail(e.target.value)} />
          </label>
        </div>
        <div>
          <label>
            Password<br />
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          </label>
        </div>
        <button type="submit" className="button primary">Sign up</button>
      </form>
      <p className="message">{message}</p>
    </div>
  );
}

function Shop({ user }) {
  const [items, setItems] = useState([]);
  const [message, setMessage] = useState('Loading shop items...');

  useEffect(() => {
    if (!user) {
      setMessage('Please sign in to view the shop.');
      return;
    }

    fetch(`${API_BASE}/api/items`, { credentials: 'include' })
      .then((response) => response.json())
      .then((data) => {
        setItems(data);
        setMessage('Browse Kenyan items.');
      })
      .catch(() => {
        setMessage('Unable to load items.');
      });
  }, [user]);

  const buyItem = (itemId) => {
    fetch(`${API_BASE}/api/purchases`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ item_id: itemId, quantity: 1 }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          setMessage(data.error);
        } else {
          setMessage('Purchase completed.');
          setItems((prevItems) =>
            prevItems.map((item) =>
              item.id === itemId ? { ...item, stock: item.stock - 1 } : item
            )
          );
        }
      })
      .catch(() => {
        setMessage('Unable to complete purchase.');
      });
  };

  if (!user) {
    return (
      <div className="panel">
        <h2>Shop</h2>
        <p>Please sign in to access the shop.</p>
      </div>
    );
  }

  return (
    <div className="panel">
      <h2>Shop</h2>
      <p className="message">{message}</p>
      <div className="card-grid">
        {items.map((item) => (
          <div key={item.id} className="card">
            <h3>{item.name}</h3>
            <p>{item.description}</p>
            <p><strong>Price:</strong> Ksh {item.price.toFixed(2)}</p>
            <p><strong>Stock:</strong> {item.stock}</p>
            <button className="button primary" onClick={() => buyItem(item.id)} disabled={item.stock < 1}>
              {item.stock > 0 ? 'Buy' : 'Sold out'}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

function PurchaseHistory({ user }) {
  const [purchases, setPurchases] = useState([]);
  const [message, setMessage] = useState('Loading purchase history...');

  useEffect(() => {
    if (!user) {
      setMessage('Please sign in to view purchase history.');
      return;
    }

    fetch(`${API_BASE}/api/purchases`, { credentials: 'include' })
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          setMessage(data.error);
        } else {
          setPurchases(data);
          setMessage('Your purchases.');
        }
      })
      .catch(() => {
        setMessage('Unable to load purchase history.');
      });
  }, [user]);

  if (!user) {
    return (
      <div className="panel">
        <h2>Purchase History</h2>
        <p>Please sign in to access purchase history.</p>
      </div>
    );
  }

  return (
    <div className="panel">
      <h2>Purchase History</h2>
      <p className="message">{message}</p>
      <div className="card-grid">
        {purchases.map((purchase) => (
          <div key={purchase.id} className="card">
            <h3>{purchase.item?.name || 'Unknown item'}</h3>
            <p>Quantity: {purchase.quantity}</p>
            <p>Total: Ksh {purchase.total_price.toFixed(2)}</p>
            <p>Date: {new Date(purchase.purchased_at).toLocaleString()}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function App() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    fetch(`${API_BASE}/api/auth/user`, { credentials: 'include' })
      .then((res) => res.json())
      .then((data) => {
        if (!data.error) {
          setUser(data);
        }
      })
      .catch(() => {});
  }, []);

  const navigate = useNavigate();

  const handleLogout = () => {
    fetch(`${API_BASE}/api/auth/logout`, {
      method: 'POST',
      credentials: 'include',
    })
      .then(() => {
        setUser(null);
        navigate('/');
      })
      .catch(() => {
        setUser(null);
        navigate('/');
      });
  };

  return (
    <div className="app-shell">
      <header className="app-header">
        <nav className="nav">
          <NavLink to="/" className="nav-link">Home</NavLink>
          <NavLink to="/shop" className="nav-link">Shop</NavLink>
          <NavLink to="/purchase-history" className="nav-link">Purchase History</NavLink>
          {!user ? (
            <>
              <NavLink to="/login" className="nav-link">Login</NavLink>
              <NavLink to="/signup" className="nav-link">Signup</NavLink>
            </>
          ) : (
            <button type="button" onClick={handleLogout} className="nav-button">
              Logout
            </button>
          )}
        </nav>
      </header>

      <main className="main-content">
        <Routes>
          <Route path="/" element={<Home user={user} />} />
          <Route path="/shop" element={<Shop user={user} />} />
          <Route path="/purchase-history" element={<PurchaseHistory user={user} />} />
          <Route path="/login" element={<Login onLogin={setUser} />} />
          <Route path="/signup" element={<Signup />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
