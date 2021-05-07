import React, {useEffect, useState} from "react";
import {useAuth0} from "@auth0/auth0-react";
import {Link} from "react-router-dom";

const Settings = () => {

    const { user, getAccessTokenSilently } = useAuth0();

    const [isAbort, setIsAbort] = useState(false)

    const [binanceapikey, setBinanceAPIKey] = useState("")
    const [binanceapisecret, setBinanceAPISecret] = useState("")
    const [kucoinapikey, setKucoinAPIKey] = useState("")
    const [kucoinapisecret, setKucoinAPISecret] = useState("")
    const [kucoinapipassphrase, setKucoinAPIPassphrase] = useState("")

    const [platform, setPlatform] = useState("")
    const [discordChannelDictionary, setDiscordChannelDictionary] = useState({})
    const [telegramChannelDictionary, setTelegramChannelDictionary] = useState({})
    const [inputID, setInputID] = useState("")
    const [inputName, setInputName] = useState("")

    const [binanceButtonColor, setBinanceButtonColor] = useState("#F5475D")
    const [kucoinButtonColor, setKucoinButtonColor] = useState("#F5475D")

    const discordButtonStyle = {
        background: `${binanceButtonColor}`,
        fontSize: "14px",
        width: "49%",
        height: "35px",
    }
    const telegramButtonStyle = {
        backgroundColor: `${kucoinButtonColor}`,
        fontSize: "14px",
        width: "49%",
        height: "35px",
    }
    const addButtonStyle = {
        backgroundColor: "#10CB81",
        fontSize: "14px",
        width: "100%",
        height: "50px",
    }
    const saveButtonStyle = {
        backgroundColor: "#10CB81",
        fontSize: "14px",
        width: "100%",
        height: "70px",
    }
    const inputFieldStyle = {
        backgroundImage: "url('./assets/icons/key.png')",
        backgroundSize: "20px",
        backgroundPosition: "5px 8px",
        backgroundRepeat: "no-repeat",
        backgroundColor: "#efb90a",
        paddingLeft: "30px",
        height: "35px",
        fontSize: "15px",
        width: "100%",
    }
    const channelBoxStyle = {
        fontFamily: "Ubuntu, sans-serif",
        display: "flex",
        flexDirection: "column",
        justifyContent: "flex-start",
        backgroundColor: "#12161B",
        color: "#ffffff",
        borderRadius: "12px",
        padding: "10px",
        margin: "1%",
        float: "left",
        minWidth: "300px",
        minHeight: "300px",
    }

    useEffect(() => {

        const getCredentials = async () => {
            try {
                const accessToken = await getAccessTokenSilently({
                    audience: "botqoin",
                    scope: "read:all",
                });

                const response = await fetch("/api/get_credentials", {
                    headers: {
                        Authorization: `Bearer ${accessToken}`,
                    },
                });

                if (isAbort === false) {
                    const credentials = await response.json()
                    setBinanceAPIKey(credentials.binance_api_key)
                    setBinanceAPISecret(credentials.binance_api_secret)
                    setKucoinAPIKey(credentials.kucoin_api_key)
                    setKucoinAPISecret(credentials.kucoin_api_secret)
                    setKucoinAPIPassphrase(credentials.kucoin_api_secret)
                }


            } catch (e) {
                console.log(e.message);
            }
        }

        const getChannels = async () => {
            const accessToken = await getAccessTokenSilently({
                    audience: `botqoin`,
                    scope: "read:all",
                });

            fetch("/api/get_channels", {
                method: 'get',
                headers: {
                    Authorization: `Bearer ${accessToken}`,
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    "Content-Type": "application/json",
                }
            })
            .then((respond => respond.json()))
            .then((data) => {
                setDiscordChannelDictionary(data.discord_channels)
                setTelegramChannelDictionary(data.telegram_channels)
            })
            .catch((error) => {
                console.log(error);
            })
        }

        getChannels().then(null)
        getCredentials().then(null)

        return () => {
            setIsAbort(true)
        }

    }, [getAccessTokenSilently, isAbort])

    const saveCredentials = async () => {

        let credentials = {
            binance_api_key: binanceapikey,
            binance_api_secret: binanceapisecret,
            kucoin_api_key: kucoinapikey,
            kucoin_api_secret: kucoinapisecret,
            kucoin_api_passphrase: kucoinapipassphrase
        }

        try {
          const accessToken = await getAccessTokenSilently({
            audience: "botqoin",
            scope: "read:all",
          });

          await fetch("/api/save_credentials", {
              method: "POST",
              headers: {
                  Authorization: `Bearer ${accessToken}`,
                  "content-type": "application/json"
              },
              body: JSON.stringify(credentials)
          });
        } catch (error) {
          console.log(error.message);
        }
      };

    const saveChannels = async () => {

        const accessToken = await getAccessTokenSilently({
             audience: `botqoin`,
             scope: "read:all",
        });

        let channels = {
            "discord_channels": discordChannelDictionary,
            "telegram_channels": telegramChannelDictionary
        }

        await fetch('/api/save_channels', {
                method: 'post',
                headers: {
                    Authorization: `Bearer ${accessToken}`,
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(channels),
            })
                .then((respond => respond.json()))
                .then((data) => {
                    console.log(data)
                })
                .catch((error) => {
                    console.log(error);
                });
    }

    const addChannels = () => {
        if (platform === "Discord") {
            let newDiscordChannelDictionary = {}
            for (const [key, value] of Object.entries(discordChannelDictionary)) {
                newDiscordChannelDictionary[key] = value
            }
            newDiscordChannelDictionary[inputID] = inputName
            setDiscordChannelDictionary(newDiscordChannelDictionary)

        } else if (platform === "Telegram") {
            let newTelegramChannelDictionary = {}
            for (const [key, value] of Object.entries(telegramChannelDictionary)) {
                newTelegramChannelDictionary[key] = value
            }
            newTelegramChannelDictionary[inputID] = inputName
            setTelegramChannelDictionary(newTelegramChannelDictionary)
        }
    }

    const removeDiscordChannel = (event) => {
        let newDiscordChannelDictionary = {}
        for (const [key, value] of Object.entries(discordChannelDictionary)) {
            if (key !== event.target.id) {
                newDiscordChannelDictionary[key] = value
            }
        }
        setDiscordChannelDictionary(newDiscordChannelDictionary)
    }

    const removeTelegramChannel = (event) => {
        let newTelegramChannelDictionary = {}
        for (const [key, value] of Object.entries(telegramChannelDictionary)) {
            if (key !== event.target.id) {
                newTelegramChannelDictionary[key] = value
            }
        }
        setTelegramChannelDictionary(newTelegramChannelDictionary)
    }

    const handleDiscordButtonClick = () => {
        setBinanceButtonColor("#10CB81")
        setKucoinButtonColor("#F5475D")
        setPlatform("Discord")
    }

    const handleTelegramButtonClick = () => {
        setKucoinButtonColor("#10CB81")
        setBinanceButtonColor("#F5475D")
        setPlatform("Telegram")
    }

    const handleInputIDChange = (value) => {
        setInputID(value.target.value)
    }

    const handleInputNameChange = (value) => {
        setInputName(value.target.value)
    }

    const ChannelBox = (props) => {
        return <div style={channelBoxStyle}>
                {Object.entries(props.dictionary).map((keyvalue) => {
                    return <p onClick={props.removeFunction} id={keyvalue[0]}>{keyvalue[1] + ": "+ keyvalue[0]}</p>
                })}
               </div>
    }

    return(
        <div>
            <Link to="/monitor">
                    <button className="menubutton" style={{position: "absolute", right: "150px", top: "20px"}}>Monitor</button>
            </Link>
            <ChannelBox removeFunction={removeDiscordChannel} dictionary={discordChannelDictionary}/>
            <ChannelBox removeFunction={removeTelegramChannel} dictionary={telegramChannelDictionary}/>
            <div className="messagebox">
                <span style={{display: "flex", justifyContent: "space-between"}}>
                    <button className="generalbutton" style={discordButtonStyle} onClick={handleDiscordButtonClick}>Discord</button>
                    <button className="generalbutton" style={telegramButtonStyle} onClick={handleTelegramButtonClick}>Telegram</button>
                </span>
                <input className="generalinput" style={inputFieldStyle} onChange={handleInputIDChange} placeholder="Channel ID/Username"/>
                <input className="generalinput" style={inputFieldStyle} onChange={handleInputNameChange} placeholder="Channel Name/Info"/>
                <button className="generalbutton" style={addButtonStyle} onClick={addChannels}>Add Channel</button>
                <button className="generalbutton" style={saveButtonStyle} onClick={saveChannels}>Save Channels</button>
            </div>
            <div className="messagebox">
                <h1>{user.name}</h1>
                <p>{user.email}</p>
                <input className="generalinput" value={binanceapikey} placeholder="Binance API Key" onChange={(event) => {setBinanceAPIKey(event.target.value)}}/>
                <input className="generalinput" value={binanceapisecret} placeholder="Binance API Secret" onChange={(event) => {setBinanceAPISecret(event.target.value)}}/>
                <input className="generalinput" value={kucoinapikey} placeholder="Kucoin API Key" onChange={(event) => {setKucoinAPIKey(event.target.value)}}/>
                <input className="generalinput" value={kucoinapisecret} placeholder="Kucoin API Secret" onChange={(event) => {setKucoinAPISecret(event.target.value)}}/>
                <input className="generalinput" value={kucoinapipassphrase} placeholder="Kucoin API Passphrase" onChange={(event) => {setKucoinAPIPassphrase(event.target.value)}}/>
                <button className="generalbutton" onClick={saveCredentials}>Save Credentials</button>
            </div>
        </div>
    )
}

export default Settings