import React from "react";
import { Switch, Route } from "react-router-dom";
import ProtectedRoute from "./protected-route";

import Monitor from "./Monitor";
import Settings from "./Settings";
import Home from "./Home";

const Main = () => {
    return (
        <Switch>
            <Route exact path="/" component={Home} />
            <ProtectedRoute path="/monitor" component={Monitor} />
            <ProtectedRoute path="/settings" component={Settings}/>
        </Switch>
    )
}

export default Main;