# Hiago Oliveira e Isaura Koch
# Trabalho G1 - Computação Gráfica, IMED
import cv2 # importa biblioteca opencv-python
import numpy as np # importa biblioteca numpy
import pyautogui # importa biblioteca pyautogui
from typing import Callable, Tuple # importa tipos de dados
from time import sleep # importa função de tempo


class MouseMove: # Criação da classe
    def __init__(self, cam_position: int):  # Método construtor da classe
        self.__cam = cv2.VideoCapture(cam_position)  # Obtém captura de câmera

        self.__blue_hsv = (  # Atribui lower e upper para identificação da cor azul
            np.array([97, 100, 117]),  # Lower
            np.array([117, 255, 255]),  # Upper
        )
        self.__green_hsv = (  # Atribui lower e upper para identificação da cor verde
            np.array([46, 99, 132]),  # Lower
            np.array([66, 255, 255])  # Upper
        )
        self.__purple_hsv = (  # Atribui lower e upper para identificação da cor roxa
            np.array([117, 21, 150]),  # Lower
            np.array([179, 255, 255])  # Upper
        )
        self.__yellow_hsv = (  # Atribui lower e upper para identificação da cor amarela
            np.array([5, 125, 209]),  # Lower
            np.array([40, 255, 255])  # Upper
        )

        self.__commands = dict(  # Atribui dicionário contendo comandos
            cursor_follow_color=self.__cursor_follow_color_command,  # Adiciona chave para função que faz o cursor seguir a cor
            left_button=self.__left_button_command,  # Adiciona chave para função que simula clique esquerdo do mouse
            right_button=self.__right_button_command,  # Adiciona chave para função que simula clique direito do mouse
            double_click=self.__double_click_command,  # Adiciona chave para função que simula clique duplo do mouse
            stop_execution=self.__stop_execution_command,  # Adiciona chave para função que faz o programa encerrar
            last_command_used=None  # Adiciona chave para log de última ação executada
        )
        self.__mouse_position = pyautogui.position()  # Obtém posição atual do cursor no sistema

    def run(self) -> None:
        '''Função principal da classe, responsável pela execução em tempo real do programa'''
        is_running = bool(
            self.__commands['last_command_used'] !=
            self.__stop_execution_command.__name__
        )  # Variável booleana para controle do laço de repetição while
        while is_running:  # Laço de repetição
            _, frame = self.__cam.read()  # Lê imagem/frame capturada pela câmera
            frame = cv2.flip(frame, 1)  # Inverte imagem/frame na horizontal
            command: Callable = self.__get_command_by_color_in_frame(frame)  # Obtém comando a ser executado

            if command:  # Verifica existência de comando
                command()  # Executa o comando
                self.__commands['last_command_used'] = command.__name__  # Salva nome do comando utilizado

            print(
                '[INFO] '
                f"Last Command Used: {self.__commands['last_command_used']}"
            )  # Loga último comando utilizado

            cv2.imshow(
                "Executando comandos do mouse com cores |"
                "Trabalho G1 | Hiago e Isaura",
                frame
            )  # Mostra resultado da imagem/frame processado em uma janela

            stop_execution = bool(
                cv2.waitKey(1) == ord('q') or
                self.__commands['stop_execution'].__name__ ==
                self.__commands['last_command_used']
            )  # Variável booleana para controle de quando parar a execução do programa
            if stop_execution:  # Condicional para parar a execução do programa
                sleep(0.5)  # Espera 5 milissegundos
                break  # Para o laço de repetição

    def __get_command_by_color_in_frame(self, frame) -> Callable:
        '''Função responsável por obter um comando a partir de uma cor capturada na imagem/frame'''
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # Transforma imagem/frame em padrão de cores HSV
        has_blue_in_frame, _ = self.__identify_color(
            frame,
            hsv_frame,
            self.__blue_hsv
        )  # Verifica se a cor azul está presente na imagem/frame
        has_green_in_frame, position = self.__identify_color(
            frame,
            hsv_frame,
            self.__green_hsv
        )  # Verifica se a cor verde está presente na imagem/frame e obtém a posição da mesma
        has_yellow_in_frame, _ = self.__identify_color(
            frame,
            hsv_frame,
            self.__yellow_hsv
        )  # Verifica se a cor amarela está presente na imagem/frame
        has_purple_in_frame, _ = self.__identify_color(
            frame,
            hsv_frame,
            self.__purple_hsv
        )  # Verifica se a cor roxa está presente na imagem/frame

        is_double_click = bool(
            has_purple_in_frame and
            has_yellow_in_frame and
            '__double_click_command' != self.__commands['last_command_used']
        )  # Variável para identificação de simulação de duplo clique a partir da presença de roxo e amarelo na imagem/frame
        is_right_button = bool(
            has_purple_in_frame and
            '__right_button_command' != self.__commands['last_command_used']
        )  # Variável para identificação de simulação de clique com botão direito do mouse a partir da presença de roxo na imagem/frame
        is_left_button = bool(
            has_yellow_in_frame and
            '__left_button_command' != self.__commands['last_command_used']
        )  # Variável para identificação de simulação de clique com botão esquerdo do mouse a partir da presença de amarelo na imagem/frame
        is_cursor_follow_color = bool(
            not has_purple_in_frame and
            not has_yellow_in_frame and
            has_green_in_frame
        )   # Variável para identificação para simulação de movimento do cursor a partir da ausência de amarelo e roxo e da presença de verde na imagem/frame
        if is_double_click:  # Verifica se o comando é de simulação de duplo clique
            return self.__commands['double_click']  # Retorna comando de duplo clique
        elif is_right_button:  # Verifica se o comando é de simulação de clique com botão direito
            return self.__commands['right_button']  # Retorna comando de simulação de clique com botão direito
        elif is_left_button:  # Verifica se o comando é de simulação de clique com botão esquerdo
            return self.__commands['left_button']  # Retorna comando de simulação de clique com botão esquerdo
        elif has_blue_in_frame:  # Verifica se o comando é para parar a execução do programa
            return self.__commands['stop_execution']  # Retorna comando que para a execução do programa
        elif is_cursor_follow_color:  # Verifica se o comando é para cursor seguir a cor
            self.__mouse_position = position  # Atribui posição da cor como posição do cursor do mouse
            return self.__commands['cursor_follow_color']  # Retorna comando para cursor seguir a cor

    def __identify_color(self, frame, frame_hsv, color_hsv) -> Tuple[bool, tuple]:
        '''Função responsável por identificar cor na imagem/frame'''
        mask = cv2.inRange(frame_hsv, *color_hsv)  # Obtém máscara aplicada na imagem/frame para uma cor em hsv
        _, border = cv2.threshold(
            cv2.cvtColor(
                cv2.bitwise_and(frame, frame, mask=mask),  # Obtém os objetos que contenham a cor na imagem/frame
                cv2.COLOR_BGR2GRAY
            ),  # Transforma imagem/frame em tons de cinza
            3,
            255,
            cv2.THRESH_BINARY
        )  # Processa imagem/frame pela função limiar
        contours, _ = cv2.findContours(
            border,
            cv2.RETR_LIST,
            cv2.CHAIN_APPROX_SIMPLE
        )  # Busca e obtém pelos contornos da imagem/frame processado

        found_color = False  # Inicializa variável para indicativo de cor encontrada
        color_position = ()  # Inicializa variável para posição da cor encontrada
        for contour in contours:  # Laço de repetição nos contornos encontrados
            area = cv2.contourArea(contour)  # Obtém a área do contorno
            x, y, width, height = cv2.boundingRect(contour)  # Obtém altura, largura e posição x e y do contorno
            if area > 500:  # Verifica se a área contornada é maior que 500
                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + width, y + height),
                    (0, 0, 0),
                    4
                )  # Desenha contorno na imagem/frama da cor encontrada
                found_color = True  # Atribui valor verdadeira para indicativo de cor encontrada
                color_position = x, y  # Atribui posição da cor encontrada
        return found_color, color_position  # Retorna indicativo de cor encontrada e posição da mesma

    def __cursor_follow_color_command(self) -> None:
        '''Função responsável por movimentar o cursor do mouse para uma determinada posição'''
        color_x_position, color_y_position = self.__mouse_position  # Extrai nova posição (x e y) do cursor
        if pyautogui.onScreen(color_x_position, color_y_position):  # Verifica se a nova posição está dentro da tela do sistema
            pyautogui.moveTo(color_x_position, color_y_position)  # Move o cursor do mouse para a nova posição

    def __left_button_command(self) -> None:
        '''Função responsável por simular clique com botão esquerdo do mouse'''
        pyautogui.click(button=pyautogui.LEFT)  # Simula clique com botão esquerdo do mouse

    def __right_button_command(self) -> None:
        '''Função responsável por simular clique com botão direito do mouse'''
        pyautogui.click(button=pyautogui.RIGHT)  # Simula clique com botão direito do mouse

    def __double_click_command(self) -> None:
        '''Função responsável por simular duplo clique do mouse'''
        pyautogui.doubleClick()  # Simula duplo clique do mouse

    def __stop_execution_command(self) -> None:
        '''Função responsável por parar execução do programa'''
        cv2.destroyAllWindows()  # Fecha todas as janelas do programa


if __name__ == '__main__':  # Verifica se o nome do arquivo executado é o principal
    MouseMove(2).run()  # Executa o programa com a câmera de índice 2 no sistema
