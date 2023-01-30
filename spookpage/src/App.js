import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import { Container, Row, Col } from 'react-bootstrap';
import React, { useState, useEffect } from "react";
import { w3cwebsocket as W3CWebSocket } from "websocket";

const client = new W3CWebSocket('ws://10.10.1.11:3950');
var ledStatus = new Uint8Array(5);

async function controlLed(client, index, state){
    var toSend = new Uint8Array(2);
    toSend[0] = index;
    toSend[1] = state;
    var string = new TextDecoder().decode(toSend);
    try {
        await waitForOpenConnection(client);
        client.send(string);
    } catch(err) { 
        console.error(err)
    }
}

function waitForOpenConnection(client) {
    return new Promise((resolve, reject) => {
        const maxNumberOfAttempts = 10
        const intervalTime = 500 //ms

        let currentAttempt = 0
        const interval = setInterval(() => {
            if (currentAttempt > maxNumberOfAttempts - 1) {
                clearInterval(interval)
                reject(new Error('Maximum number of attempts exceeded'))
            } else if (client.readyState === client.OPEN) {
                clearInterval(interval)
                resolve()
            }
            currentAttempt++
        }, intervalTime)
    })
}    

function displayStatus(connectionSocket){
    var returnString;
    if(connectionSocket === true)
    {
        returnString = '[connected]';
    }
    else
    {
        returnString = '[offline]';
    }
    return returnString;
}

 
const App = () => {
 
    const [connectionSocket, setConnectionSocket] = useState(null);
 
    useEffect(() => {

        client.onopen = () => {
            setConnectionSocket(true);
        };

        client.onmessage = (message) => {
            //response
            console.log(message.data.length);
            for (let i = 0; i < message.data.length; i++) {
               ledStatus[i] = message.data.charCodeAt(i);
            }
            console.log(ledStatus);
        };

        client.onclose = () => {
            setConnectionSocket(false);
        };
    }, [])


      return (
         <Container className="fullscreen">
            <Row>
               <Col>
                  <div><font color="white">{displayStatus(connectionSocket)}</font></div>
               </Col>

            </Row>

            <Row>                                                      
               <Col>                                                  
                  <button className="buttonfirst buttongreen" onClick={() => controlLed(client, 0, 1)}>
                     activate led 1                                 
                  </button>                                          

                  <button className="buttonfirst buttongreen" onClick={() => controlLed(client, 0, 0)}>
                     deactivate led 1                              
                  </button>                                          
               </Col>                                                 
            </Row>

            <Row>                                                      
               <Col>                                                  
                  <button className="buttonfirst buttongreen" onClick={() => controlLed(client, 1, 1)}>
                     activate led 2                                 
                  </button>                                          

                  <button className="buttonfirst buttongreen" onClick={() => controlLed(client, 1, 0)}>
                     deactivate led 2                              
                  </button>                                          
               </Col>                                                 
            </Row>

            <Row>                                                      
               <Col>                                                  
                  <button className="buttonfirst buttongreen" onClick={() => controlLed(client, 2, 1)}>
                     activate led 3                                 
                  </button>                                          

                  <button className="buttonfirst buttongreen" onClick={() => controlLed(client, 2, 0)}>
                     deactivate led 3                              
                  </button>                                          
               </Col>                                                 
            </Row>

            <Row>                                                      
               <Col>                                                  
                  <button className="buttonfirst buttongreen" onClick={() => controlLed(client, 3, 1)}>
                     activate led 4                                 
                  </button>                                          

                  <button className="buttonfirst buttongreen" onClick={() => controlLed(client, 3, 0)}>
                     deactivate led 4                              
                  </button>                                          
               </Col>                                                 
            </Row>

            <Row>                                                      
               <Col>                                                  
                  <button className="buttonfirst buttongreen" onClick={() => controlLed(client, 4, 1)}>
                     activate led 5                                 
                  </button>                                          

                  <button className="buttonfirst buttongreen" onClick={() => controlLed(client, 4, 0)}>
                     deactivate led 5                              
                  </button>                                          
               </Col>                                                 
            </Row>

         </Container>
      )
}

export default App;
