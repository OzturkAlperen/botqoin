import React from "react";
import AuthenticationButton from "./authButtons/authentication-buton";
import {useAuth0} from "@auth0/auth0-react";

const Header = () => {

    const { user, isAuthenticated } = useAuth0();

    const nameTag = {
        display: "flex",
        textAlign: "center",
        cursor: "default",
        position: "absolute",
        left: "280px",
        top: "10px",
        borderRadius: "12px",
        backgroundColor: "#12161B",
        color: "#10CB81",
        height: "60px",
        lineHeight: "60px",
        padding: "0px 10px",
    }

    return(
        <header className="heading" style={{display: "flex", justifyContent: "space-between", alignItems: "center"}}>

            <h1 style={{cursor: "default", margin: "10px"}}>botqoin</h1>
            <h1 className="versiontag" style={{cursor: "default", position: "absolute", left: "155px", top: "20px"}}>Alpha</h1>
            {isAuthenticated && <h1 style={nameTag}>{user.name}</h1>}
            <AuthenticationButton style={{position: "absolute", right: "20px", top: "5px"}} />

        </header>)
}

export default Header