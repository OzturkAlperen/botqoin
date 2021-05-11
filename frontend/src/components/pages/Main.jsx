import React from "react";
import { Switch, Route } from "react-router-dom";
import ProtectedRoute from "../elements/protected-route";
import {AnimatePresence} from "framer-motion";

import Bot from "./Bot";
import Settings from "./Settings";
import Home from "./Home";

const Main = () => {

    return (
        <AnimatePresence>
            <Switch>
                <Route exact path="/" component={Home} />
                <ProtectedRoute path="/bot" component={Bot} />
                <ProtectedRoute path="/settings" component={Settings}/>
            </Switch>
        </AnimatePresence>
    )
}

export default Main;