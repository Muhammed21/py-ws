# Diagramme de Sequence - Messagerie WebSocket

Ce diagramme illustre les flux de communication du projet de messagerie WebSocket.

## Flux de communication

```mermaid
sequenceDiagram
    participant C1 as Client1
    participant S as Serveur
    participant C2 as Client2

    %% Connexion Client1
    C1->>S: Connexion WebSocket
    S->>C1: RECEPTION "Bienvenue"
    C1->>S: DECLARATION (username=Client1)
    S->>C1: RECEPTION "Declaration recue"

    %% Connexion Client2
    C2->>S: Connexion WebSocket
    S->>C2: RECEPTION "Bienvenue"
    C2->>S: DECLARATION (username=Client2)
    S->>C2: RECEPTION "Declaration recue"

    %% Message au serveur
    C1->>S: ENVOI (receiver=SERVER, value="Hello")
    Note over S: Affiche le message

    %% Message entre clients
    C1->>S: ENVOI (receiver=Client2, value="Salut!")
    S->>C2: RECEPTION (emitter=Client1, value="Salut!")

    %% Reponse
    C2->>S: ENVOI (receiver=Client1, value="Hello!")
    S->>C1: RECEPTION (emitter=Client2, value="Hello!")

    %% Broadcast serveur
    S->>C1: RECEPTION (emitter=SERVER, value="Annonce")
    S->>C2: RECEPTION (emitter=SERVER, value="Annonce")

    %% Erreur destinataire inconnu
    C1->>S: ENVOI (receiver=Inconnu, value="Test")
    S->>C1: RECEPTION "Erreur: destinataire non trouve"
```

## Description des flux

### 1. Connexion d'un client
- Client -> Serveur : Connexion WebSocket
- Serveur -> Client : Message "Bienvenue" (RECEPTION)
- Client -> Serveur : Message DECLARATION (s'enregistrer avec username)
- Serveur -> Client : Confirmation de declaration (RECEPTION)

### 2. Envoi de message client -> serveur
- Client -> Serveur : Message ENVOI (receiver="SERVER")
- Le serveur affiche le message

### 3. Envoi de message client -> client
- ClientA -> Serveur : Message ENVOI (receiver="ClientB")
- Serveur -> ClientB : Message RECEPTION (forward)
- Si destinataire inconnu : Serveur -> ClientA : Message erreur

### 4. Broadcast serveur -> tous
- Serveur -> Tous les clients : Message RECEPTION

---

## Diagramme detaille - Envoi de message

Ce diagramme montre le flux interne lors de l'envoi d'un message d'un client vers un autre.

```mermaid
sequenceDiagram
    participant User as Utilisateur
    participant WC as WSClient
    participant MSG as Message
    participant WS as WebSocket
    participant SRV as WSServer
    participant DEST as Client Destinataire

    User->>WC: Saisie "Alice:Bonjour"

    rect rgb(230, 240, 255)
        Note over WC: Parsing de l'input
        WC->>WC: split(":", 1)
        WC->>WC: dest="Alice", value="Bonjour"
    end

    rect rgb(255, 245, 230)
        Note over WC,MSG: Creation du message
        WC->>MSG: new Message(ENVOI, emitter, receiver, value)
        MSG->>MSG: to_json()
        MSG-->>WC: JSON string
    end

    Note right of MSG: {"message_type": "envoi",<br/>"data": {"emitter": "Bob",<br/>"receiver": "Alice",<br/>"value": "Bonjour"}}

    WC->>WS: ws.send(json)
    WS->>SRV: WebSocket frame

    rect rgb(230, 255, 230)
        Note over SRV: Traitement serveur
        SRV->>MSG: Message.from_json(message)
        MSG-->>SRV: Message object
        SRV->>SRV: Verifier message_type == ENVOI
        SRV->>SRV: Chercher receiver dans clients{}
    end

    alt Destinataire trouve
        SRV->>MSG: new Message(RECEPTION, emitter, receiver, value)
        MSG-->>SRV: forward_msg
        SRV->>DEST: server.send_message(forward_msg.to_json())
        DEST->>DEST: on_message() - Affiche le message
    else Destinataire non trouve
        SRV->>MSG: new Message(RECEPTION, "SERVER", emitter, "Erreur...")
        MSG-->>SRV: error_msg
        SRV->>WS: server.send_message(error_msg.to_json())
        WS->>WC: WebSocket frame
        WC->>WC: on_message() - Affiche l'erreur
    end
```

## Diagramme - Structure du Message JSON

```mermaid
flowchart TB
    subgraph Message["Structure Message"]
        MT[message_type]
        DATA[data]

        subgraph DataContent["Contenu de data"]
            E[emitter]
            R[receiver]
            V[value]
        end

        DATA --> DataContent
    end

    subgraph Types["Types de message"]
        D["DECLARATION<br/>Enregistrement client"]
        EN["ENVOI<br/>Client -> Serveur"]
        RE["RECEPTION<br/>Serveur -> Client"]
    end

    MT --> Types
```

## Diagramme - Traitement selon le type de message

```mermaid
flowchart TD
    A[Message recu par serveur] --> B{message_type?}

    B -->|DECLARATION| C[Enregistrer client]
    C --> C1[clients dict emitter = client]
    C1 --> C2[Envoyer confirmation RECEPTION]

    B -->|ENVOI| D{receiver == SERVER?}
    D -->|Oui| E[Afficher message sur console serveur]
    D -->|Non| F{receiver existe?}

    F -->|Oui| G[Creer message RECEPTION]
    G --> H[Forward au destinataire]

    F -->|Non| I[Creer message erreur]
    I --> J[Envoyer erreur a emitter]
