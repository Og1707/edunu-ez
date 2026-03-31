import { useState, useEffect } from 'react';

const getStoredUser = () => {
  try {
    return JSON.parse(localStorage.getItem('user')) || null;
  } catch (error) {
    return null;
  }
};

const useAuth = () => {
  const [user, setUser] = useState(getStoredUser());

  useEffect(() => {
    const handleStorageChange = () => {
      setUser(getStoredUser());
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  const logout = () => {
    localStorage.removeItem('user');
    setUser(null);
  };

  return { user, logout };
};

export default useAuth;
