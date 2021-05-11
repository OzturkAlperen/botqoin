import React, {useEffect, useState} from "react";
import {useAuth0} from "@auth0/auth0-react";
import { motion } from "framer-motion";
import OptionButton from "../interfaces/option-button";
import KeyIcon from "../../assets/icons/key.svg";
import TagIcon from "../../assets/icons/tag.svg";
import Guide from "../interfaces/user-guide";

const Settings = () => {

    const { getAccessTokenSilently } = useAuth0();

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

    const pageVariants = {
        initial: {
            opacity: 0,
            },
        in: {
            opacity: 1,
        },
        out: {
            opacity: 0,
        }
    }

    const pageTransition = {
        duration: 0.6
    }

    const addButtonStyle = {
        backgroundColor: "#10CB81",
        fontSize: "14px",
        width: "100%",
        height: "40px",
    }
    const saveButtonStyle = {
        backgroundColor: "#10CB81",
        fontSize: "14px",
        width: "100%",
        height: "40px",
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

    const handlePlatformChange = (value) => {
        setPlatform(value)
    }

    const handleInputIDChange = (value) => {
        setInputID(value.target.value)
    }

    const handleInputNameChange = (value) => {
        setInputName(value.target.value)
    }

    const ChannelBox = (props) => {
        return( <div className="displaybox" style={{flexDirection: "column"}}>
                    <h1 style={{cursor: "default"}}>{props.name}</h1>
                    <p style={{cursor: "default"}}>━━━━━━━━━━━━━━━━━</p>
                    {Object.entries(props.dictionary).map((keyvalue) => {
                        return <p onClick={props.removeFunction} id={keyvalue[0]}>{keyvalue[1] + ": "+ keyvalue[0]}</p>
                    })}
               </div>)
    }

    return(
        <motion.div variants={pageVariants} transition={pageTransition} exit="out" animate="in" initial="initial" style={{display: "flex", justifyContent: "center", alignItems: "center", alignContent: "stretch", flexWrap: "wrap"}}>
            <ChannelBox name="Discord Channels" removeFunction={removeDiscordChannel} dictionary={discordChannelDictionary}/>
            <ChannelBox name="Telegram Channels" removeFunction={removeTelegramChannel} dictionary={telegramChannelDictionary}/>
            <div className="displaybox">
                <h1 style={{cursor: "default"}}>Edit Channels</h1>
                <p style={{cursor: "default"}}>━━━━━━━━━━━━━━━━━</p>
                <OptionButton buttons={{"Discord": "Discord", "Telegram": "Telegram"}} callback={handlePlatformChange} buttonClass="platformbutton"/>
                <span style={{display: "flex", justifyContent: "space-between"}}>
                    <input className="botinput" style={{backgroundImage: `url(${KeyIcon})`}} onChange={handleInputIDChange} placeholder="Channel ID/Username"/>
                </span>
                <span style={{display: "flex", justifyContent: "space-between"}}>
                    <input className="botinput" style={{backgroundImage: `url(${TagIcon})`}} onChange={handleInputNameChange} placeholder="Channel Name/Info"/>
                </span>
                <span style={{display: "flex", justifyContent: "space-between"}}>
                    <button className="generalbutton" style={addButtonStyle} onClick={addChannels}>Add Channel</button>
                </span>
                <span style={{display: "flex", justifyContent: "space-between"}}>
                    <button className="generalbutton" style={saveButtonStyle} onClick={saveChannels}>Save Channels</button>
                </span>
            </div>
            <div className="displaybox">
                <h1 style={{cursor: "default"}}>Exchange Credentials</h1>
                <p style={{cursor: "default"}}>━━━━━━━━━━━━━━━━━</p>
                <input className="botinput" style={{backgroundImage: `url(${KeyIcon})`}} value={binanceapikey} placeholder="Binance API Key" onChange={(event) => {setBinanceAPIKey(event.target.value)}}/>
                <input className="botinput" style={{backgroundImage: `url(${KeyIcon})`}} value={binanceapisecret} placeholder="Binance API Secret" onChange={(event) => {setBinanceAPISecret(event.target.value)}}/>
                <input className="botinput" style={{backgroundImage: `url(${KeyIcon})`}} value={kucoinapikey} placeholder="Kucoin API Key" onChange={(event) => {setKucoinAPIKey(event.target.value)}}/>
                <input className="botinput" style={{backgroundImage: `url(${KeyIcon})`}} value={kucoinapisecret} placeholder="Kucoin API Secret" onChange={(event) => {setKucoinAPISecret(event.target.value)}}/>
                <input className="botinput" style={{backgroundImage: `url(${KeyIcon})`}} value={kucoinapipassphrase} placeholder="Kucoin API Passphrase" onChange={(event) => {setKucoinAPIPassphrase(event.target.value)}}/>
                <button className="generalbutton" style={saveButtonStyle} onClick={saveCredentials}>Save Credentials</button>
            </div>
            <Guide />
        </motion.div>
    )
}

export default Settings