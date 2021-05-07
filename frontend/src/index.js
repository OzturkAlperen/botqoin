import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter } from 'react-router-dom';
import { Auth0Provider } from "@auth0/auth0-react";
import App from './components/App.jsx';

ReactDOM.render(
    <BrowserRouter>
        <Auth0Provider domain="botqoin.us.auth0.com" clientId="ko5MFeIevzSsxp5gzLnJe6DmbknPumIp" redirectUri={"http://192.168.1.16:3000/monitor"} audience="botqoin" scope="read:all">
            <App />
        </Auth0Provider>
    </BrowserRouter>,
    document.getElementById('root')
);
