import React from "react";
import { Route } from "react-router-dom";
import { withAuthenticationRequired } from "@auth0/auth0-react";
import Redirection from "./Redirection";

const ProtectedRoute = ({ component, ...args }) => (
  <Route
    component={withAuthenticationRequired(component, {
      onRedirecting: () => <Redirection />,
        returnTo: window.location.origin
    })}
    {...args}
  />
);

export default ProtectedRoute;