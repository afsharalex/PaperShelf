import React from 'react';
import { NavLink } from 'react-router-dom';

const Navbar = () => {
  return (
    <div className="nav-tabs">
      <NavLink to="/" className={({ isActive }) => isActive ? "nav-tab active" : "nav-tab"}>
        Home
      </NavLink>
      <NavLink to="/upload-page" className={({ isActive }) => isActive ? "nav-tab active" : "nav-tab"}>
        Upload Papers
      </NavLink>
      <NavLink to="/query-page" className={({ isActive }) => isActive ? "nav-tab active" : "nav-tab"}>
        Query Papers
      </NavLink>
    </div>
  );
};

export default Navbar;