import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter } from 'react-router-dom'
import { Auth0Provider } from "@auth0/auth0-react";
import App from './components/pages/App.jsx';

ReactDOM.render(
    <BrowserRouter>
        <Auth0Provider domain="botqoin.us.auth0.com" clientId="ko5MFeIevzSsxp5gzLnJe6DmbknPumIp" redirectUri={"http://botqoin.tech/"} audience="botqoin" scope="read:all">
            <App />
        </Auth0Provider>
    </BrowserRouter>,
    document.getElementById('root')
);
