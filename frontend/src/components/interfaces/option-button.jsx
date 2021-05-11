import React, {createRef, useState, useEffect} from "react";

const OptionButton = ({ buttons, buttonClass, callback }) => {

    const [value, setValue] = useState()
    const refArray = []
    const buttonWidth = ((100 - (Object.keys(buttons).length - 1)) - ((100 - (Object.keys(buttons).length - 1)) % Object.keys(buttons).length)) / Object.keys(buttons).length

    useEffect(() => {
        callback(value)
    }, [value, callback])

    const select = (event) => {
        event.target.style.backgroundColor = "#10CB81"
        refArray.forEach((currentRef) => {
            if (currentRef.current.id !== event.target.id) {
                currentRef.current.style.backgroundColor = "#F5475D"
            }
        })
        setValue(event.target.id)
    }

    return(
        <span style={{display: "flex", justifyContent: "space-between"}}>
            {Object.entries(buttons).map((keyvalue) => {
                const newRef = createRef()
                refArray.push(newRef)
                return <button ref={newRef} id={keyvalue[0]} key={keyvalue[0]} className={buttonClass} onClick={select} style={{width: `${buttonWidth}%`}}>{keyvalue[1]}</button>
            })}
        </span>
    )
}

export default OptionButton
