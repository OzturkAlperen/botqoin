import React, { createRef } from "react";
import {Link} from "react-router-dom";
import { useAuth0 } from "@auth0/auth0-react";


const Navbar = (props) => {
    return(
        <div>
            <nav className="navbar">
                <ul className="navbar-nav" style={{listStyle: "none", margin: 0, padding: 0}}> { props.children } </ul>
            </nav>

        </div>
    )
}

const NavItem = (props) => {
    const dropdown = createRef()

    const handleDropdown = () => {
        if (dropdown.current.style.visibility === "hidden") {
            dropdown.current.style.visibility = "visible"
            dropdown.current.style.opacity = "1"

        } else {
            dropdown.current.style.opacity = "0"
            dropdown.current.style.visibility = "hidden"
        }
    }

    return(
        <li className="nav-item">
            <div className="icon-button" onClick={handleDropdown} style={{backgroundImage: `url(${props.icon})`}} />
            <div ref={dropdown} className="dropdown" style={{visibility: "hidden", opacity: 0}}>{props.children}</div>
        </li>
    )
}

const NavHeading = (props) => {
    return(
        <h1 className="nav-heading">{props.name}</h1>
    )
}

const DropdownMenu = () => {

    const { loginWithRedirect, logout, isAuthenticated } = useAuth0();

    const DropdownItem = (props) => {
        return(
            <Link to={props.route} className="menu-item" onClick={props.onClick}>
                {props.children}
            </Link>
        );
    }

    return(
        <span>
            <DropdownItem route="/bot">Bot</DropdownItem>
            <DropdownItem route="/settings">Settings</DropdownItem>
            {isAuthenticated ? <DropdownItem route="#" onClick={logout}>Logout</DropdownItem>:
            <DropdownItem route="#" onClick={loginWithRedirect}>Login</DropdownItem>}
        </span>
    )
}

export default Navbar
export { NavItem, NavHeading, DropdownMenu }