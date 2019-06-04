
import math
import socketio
import copy

tileRep = ['_', 'X', 'O']
N = 8
boardsize = 64

#8 direcciones en la que estas se puede mover
pos_x = [-1, 0, 1,-1, 1,-1,0,1]
pos_y = [-1,-1,-1, 0, 0, 1,1,1]
def ix(row, col):
    return (row-1)*N + 'abcdefgh'.index(col)


##crea los movimientos especificos
def makeMove(board, x, y, player):
    opponent = 0 
    board[x + N *y] = player
    for d in range(8):
        i = 0
        for i in range(N):
            dx = x + pos_x[d] * (i + 1)
            dy = y + pos_y[d] * (i + 1)
            if dx < 0 or dx > N - 1 or dy < 0 or dy > N - 1:
                i = 0
                break
            elif board[dy*N + dx] == player:
                break
            elif board[dy*N + dx] == 0:
                i = 0
                break
            else:
                i += 1
        for i in range(i):
            dx = x + pos_x[d] * (i + 1)
            dy = y + pos_y[d] * (i + 1)
            board[dy*N + dx] = player
        opponent+= i
    return (board, opponent)

##Nos crea el board
def humanBoard(board):
    result = 'A B C D E F G H'
    for i in range(len(board)):
        if i%N == 0:
            result += '\n \n' + str((int(math.floor(i/N)) + 1 )) + ' '
        
        result += ' ' + tileRep[board[i]] + ' '
        
    return result


##Revisa que movimiento es valifo en todo el board
def isValidMove(board, tile, x, y):
    index = x * N + y
    
    if board[index] != 0 or not onBoard(x, y):
        return False

    testboard = copy.deepcopy(board)
    testboard[index] = tile

    otherTile = 1
    if tile == 1:
        otherTile = 2

    flip = []
    nextMoves = []
    for xd, yd in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
        i, j = x, y

        i += xd
        j += yd
        if onBoard(i, j) and testboard[i*N+j] == otherTile:
            i += xd
            j += yd
            if not onBoard(i, j):
                continue
            while testboard[i*N + j] == otherTile:
                i += xd
                j += yd

                if not onBoard(i, j):
                    break
            if not onBoard(i, j):
                continue
            if testboard[i*N + j] == tile:
                while True:
                    i -= xd
                    j -= yd

                    if i == x and j == y:
                        break
                    flip.append([i, j])
                    nextMoves.append([x, y])

    if len(flip) > 0: 
        for i in flip : 
            testboard[i[0] * N + i[1]] = tile
        return testboard, nextMoves
    else:

        return False


##Revisa los movimientos posibles de la funcion anterior pero esta vez si revisa los que estan al rededor en nuestra tabla
def posiblesMovimientos(board):
    posible = []
    final = []
    for x in range(0, 8):
        for y in range(0, 8):
            ##chequea los movimientos y los ingresa a la lista
            moving = isValidMove(board, 1, x, y)
            posible.append(moving)
    for n in range(len(posible)):
        ##quita los que no son posibles
        if posible[n] != False:
            final.append(posible[n])
    return final 

def validateHumanPosition(position):
    validated = len(position) == 2
    
    if validated:
        row = int(position[0])
        col = position[1].lower()
        return (1 <= row and row <= N) and ('abcdefgh'.index(col) >= 0)
    
    else:
        return False


##Nos indica si estamos dentro del tablero
def onBoard(x, y):
    return x >= 0 and x <= 7 and y >= 0 and y <=7


##funcion de alphabeta 
def alphaBeta(board, depht, a, b, maximizingPlayer, tile):
    testboard = [] 
    movimientos = posiblesMovimientos(board)
    for z in range(len(movimientos)):
        testboard.append(movimientos[z][0])

    ##Chequea que sea max
    if maximizingPlayer == True:
        for n in testboard:
            a = max(a, alphabeta(n, depht - 1, a, b, False, tile))
            if a >= b:
                break
 
        return a
    ##cheqea que sea min 
    elif maximizingPlayer == False:
        for n in testboard:
            b = min(b, alphabeta(n, depht - 1, a, b, True, tile))
            if a >= b:
                break
  
        return b

##Nos dice cual es el mejor movimiento para nuestro board 
def bestMovement(board, player):	
    x = posiblesMovimientos(board)
    best = 0
    mejor = 0
    puntos = 0

    for i in range(len(x)):
        ##Nos da la posicion en Y, se utiliza math.floor para redondear el numoro

        print("c")
        positiony = x[1][i]
        ##Nos da la posicion en X 
        positionx =  x[1][i]
        ##Revisa los puntos a relaizar 
        puntos =alphaBeta(board, player, 5, -99999, 99999, True)

        ##Revisa que moviiento guardado en la lista es la mejor opcion
        if(puntos >= mejor):
            mejor = puntos
            best = i
			
    return  print(x[best][best])
        

#Se crea el socket en donde se conectara mi computadora y se conecta al IP 192.168.88.252
socket = socketio.Client()
##IP a conectar
socket.connect('http://localhost:4000')
userName = 'Michelle Bloomfield '
##Tournament ID dado por el catedratico
tournamentID = 12
print("Se conecto : " + userName)

##Cuando se conecta hay un emit al servidor con el protocolo siguiente
@socket.on('connect')
def on_connect():
    socket.emit('signin',{
            'user_name': userName,
            'tournament_id': tournamentID,
            'user_role': 'player'

        })

##Recibe instruciones
@socket.on('ready')
def on_ready(data):


    columnas = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    filas = ['1', '2', '3', '4', '5', '6', '7', '8']

    best = bestMovement(data['board'], data['player_turn_id'])
    ##Realiza movimiento random a random_filas y random_columnas
    movement = filas[best[0]] + columnas[best[1]]

        
    socket.emit('play',{
        'player_turn_id': data['player_turn_id'],
        'tournament_id': tournamentID,
        'game_id': data['game_id'],
        'movement': ix(int(movement[0]), movement[1].lower())
        })


@socket.on('finish')
def ready(data):
    print("Game " + str(data['game_id']) + " has finished")
    print("Ready to play again!")

    socket.emit('player_ready',{
        'tournament_id': tournamentID,
        'game_id': data['game_id'],
        'player_turn_id': data['player_turn_id']
      })

