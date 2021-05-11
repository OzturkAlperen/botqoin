import React, { useState, useEffect } from "react";
import BitcoinIcon from "../../assets/icons/bitcoin.svg";
import EthereumIcon from "../../assets/icons/ethereum.svg";
import LitecoinIcon from "../../assets/icons/litecoin.svg";
import ChainlinkIcon from "../../assets/icons/chainlink.svg";
import StellarIcon from "../../assets/icons/stellar.svg";

function Prices() {
  const [priceBTC, setPriceBTC] = useState();
  const [priceETH, setPriceETH] = useState();
  const [priceLTC, setPriceLTC] = useState();
  const [priceLINK, setPriceLINK] = useState();
  const [priceXLM, setPriceXLM] = useState();

  useEffect(() => {

    let websocket = new WebSocket("wss://ws-feed.pro.coinbase.com");

    websocket.onopen = () => {
      let msg = {
      type: "subscribe",
      product_ids: ["BTC-USD", "ETH-USD", "LTC-USD", "LINK-USD", "XLM-USD"],
      channels: ["ticker"]
    };
    let jsonMsg = JSON.stringify(msg);
    websocket.send(jsonMsg);
    }

    websocket.onmessage = (event) => {
        let data = JSON.parse(event.data);
        if (data['product_id'] === "BTC-USD") {
            setPriceBTC(data['price'])
        } else if (data['product_id'] === "ETH-USD") {
            setPriceETH(data['price'])
        } else if (data['product_id'] === "LTC-USD") {
            setPriceLTC(data['price'])
        } else if (data['product_id'] === "LINK-USD") {
            setPriceLINK(data['price'])
        } else if (data['product_id'] === "XLM-USD") {
            setPriceXLM(data['price'])
        }
    };

    return function cleanup() {
        websocket.close()
      }
  }, []);

  return (
    <div style={{display: "flex", flexDirection: "row", justifyContent: "center", flexWrap: "wrap"}}>
        <span className="displaybox-mini">
            <span style={{display: "flex", justifyContent: "center"}}>
                <img style={{width: "40px", marginRight: "20px"}} src={BitcoinIcon} alt="Bitcoin" />
                <h1 style={{cursor: "default"}}>BTC-USD</h1>
            </span>
            <p style={{cursor: "default"}}>━━━━━━━━━━━━━━━━━</p>
            <h1>{priceBTC}</h1>
        </span>
        <span className="displaybox-mini">
            <span style={{display: "flex", justifyContent: "center"}}>
                <img style={{width: "30px", marginRight: "20px"}} src={EthereumIcon} alt="Ethereum" />
                <h1 style={{cursor: "default"}}>ETH-USD</h1>
            </span>
            <p style={{cursor: "default"}}>━━━━━━━━━━━━━━━━━</p>
            <h1>{priceETH}</h1>
        </span>
        <span className="displaybox-mini">
            <span style={{display: "flex", justifyContent: "center"}}>
                <img style={{width: "40px", marginRight: "20px"}} src={LitecoinIcon} alt="Litecoin" />
                <h1 style={{cursor: "default"}}>LTC-USD</h1>
            </span>
            <p style={{cursor: "default"}}>━━━━━━━━━━━━━━━━━</p>
            <h1>{priceLTC}</h1>
        </span>
        <span className="displaybox-mini">
            <span style={{display: "flex", justifyContent: "center"}}>
                <img style={{width: "35px", marginRight: "20px"}} src={ChainlinkIcon} alt="Chainlink"/>
                <h1 style={{cursor: "default"}}>LINK-USD</h1>
            </span>
            <p style={{cursor: "default"}}>━━━━━━━━━━━━━━━━━</p>
            <h1>{priceLINK}</h1>
        </span>
        <span className="displaybox-mini">
            <span style={{display: "flex", justifyContent: "center"}}>
                <img style={{width: "40px", marginRight: "20px"}} src={StellarIcon} alt="Stellar Lumens" />
                <h1 style={{cursor: "default"}}>XLM-USD</h1>
            </span>
            <p style={{cursor: "default"}}>━━━━━━━━━━━━━━━━━</p>
            <h1>{priceXLM}</h1>
        </span>
    </div>
  );
}

export default Prices