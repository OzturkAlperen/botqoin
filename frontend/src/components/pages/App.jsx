import React from "react";
import Main from "./Main.jsx";
import Navbar, { NavItem, NavHeading, DropdownMenu } from "../interfaces/navigation-bar";
import MenuIcon from "../../assets/icons/menu.svg"


function App() {
    return(
            <div>
                <Navbar>
                    <NavHeading name="botqoin"/>
                    <NavItem icon={MenuIcon}>
                        <DropdownMenu />
                    </NavItem>
                </Navbar>
                <Main />
            </div>)
}

export default App