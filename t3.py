# baselineTeam.py
# ---------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


# baselineTeam.py
# ---------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html
import random
import util

from captureAgents import CaptureAgent
from game import Directions
from util import nearestPoint


#################
# Team creation #
#################

def create_team(first_index, second_index, is_red,
                first='OffensiveReflexAgent', second='DefensiveReflexAgent', num_training=0):
    """
    This function should return a list of two agents that will form the
    team, initialized using firstIndex and secondIndex as their agent
    index numbers.  isRed is True if the red team is being created, and
    will be False if the blue team is being created.

    As a potentially helpful development aid, this function can take
    additional string-valued keyword arguments ("first" and "second" are
    such arguments in the case of this function), which will come from
    the --redOpts and --blueOpts command-line arguments to capture.py.
    For the nightly contest, however, your team will be created without
    any extra arguments, so you should make sure that the default
    behavior is what you want for the nightly contest.
    """
    return [eval(first)(first_index), eval(second)(second_index)]

class ReflexCaptureAgent(CaptureAgent):
    def __init__(self, index, time_for_computing=0.1):
        super().__init__(index, time_for_computing)
        self.start = None
        self.distancer = None

    def register_initial_state(self, game_state):
        '''if self.red:
            self.middle = (game_state.data.layout.width - 2) / 2
        else:
            self.middle = (game_state.data.layout.width - 2) / 2 + 1
        self.boundary = []
        for i in range(1, game_state.data.layout.height - 1):
            if not game_state.has_wall(int(self.middle), i):
                self.boundary.append((int(self.middle), i))
        layout = game_state.data.layout
        self.distancer = layout'''
        self.start = game_state.get_agent_position(self.index)
        CaptureAgent.register_initial_state(self, game_state)

    def choose_action(self, game_state):
        '''
        food_positions = self.get_food(game_state).as_list()

        # Si no hay bolas blancas, no hay acciones que tomar
        if not food_positions:
            return Directions.STOP

        # Obtener la posición actual del Pacman
        current_position = game_state.get_agent_position(self.index)

        # Calcular la posición de la bola blanca más cercana
        closest_food = self.get_closest_food(current_position, food_positions)

        # Calcular la distancia a la bola blanca más cercana
        distance_to_food = self.manhattan_distance(current_position, closest_food)

        # Evitar a los enemigos
        enemies = self.get_opponents(game_state)
        danger_score = sum([self.evaluate_enemy_danger(game_state, enemy) for enemy in enemies])

        # Si hay peligro, evitar a los enemigos
        if danger_score > 0:
            return self.avoid_enemies(game_state)

        # Si la distancia a la comida más cercana es pequeña, ir hacia ella
        if distance_to_food < 5:
            return self.get_action_to_position(game_state, closest_food)

        # Explorar y expandir: usar A* para encontrar la mejor acción
        return self.a_star_search(game_state, current_position, closest_food)
        '''
        actions = game_state.get_legal_actions(self.index)
        values = [self.evaluate(game_state, a) for a in actions]
        max_value = max(values)
        best_actions = [a for a, v in zip(actions, values) if v == max_value]

        food_left = len(self.get_food(game_state).as_list())

        if food_left <= 2:
            best_dist = 9999
            best_action = None
            for action in actions:
                successor = self.get_successor(game_state, action) 
                pos2 = successor.get_agent_position(self.index)
                dist = self.get_maze_distance(self.start, pos2)
                if dist < best_dist:
                    best_action = action
                    best_dist = dist
            return best_action

        return random.choice(best_actions)
    
    def get_action_to_position(self, game_state, goal_position):
        current_position = game_state.get_agent_state(self.index).get_position()
        return self.a_star_search(game_state, current_position, goal_position)

    def evaluate_enemy_danger(self, game_state, enemy):
        my_state = game_state.get_agent_state(self.index)
        my_position = my_state.get_position()
        enemy_state = game_state.get_agent_state(self.index)
        enemy_position = enemy_state.get_position()
        distance_to_enemy = self.manhattan_distance(my_position, enemy_position)  # Asumiendo que `enemy` es la posición del enemigo
        danger_score = 0

        # Si el enemigo es un Pac-Man, podría representar un peligro
        if distance_to_enemy < 5:
            danger_score += 1

        return danger_score
    
    def manhattan_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    

    def get_successors(self, state):
        successors = []
        for action in state.get_legal_actions(self.index):
            successor = state.generate_successor(self.index, action)
            successors.append((successor, action))
        return successors

    def get_cost_of_action(self, state, action):
        # Puedes definir el costo según la distancia u otras métricas específicas del juego
        return 1

    def evaluate(self, game_state, action):
        # Multiplicar cada valor correspondiente de los diccionarios
        #result = sum(features[key] * weights[key] for key in features)

        features = self.get_features(game_state, action)
        weights = self.get_weights(game_state, action)

        # Dot product of features and weights
        evaluation = sum(features[key] * weights[key] for key in features)
        #evaluation=features*weights
        return evaluation

    def get_features(self, game_state, action):
        # Puedes definir características basadas en la posición, el estado del juego, etc.
        features = util.Counter()
        successor = self.get_successor(game_state, action)
        features['successor_score'] = self.get_score(successor)
        return features

    def get_weights(self, game_state, action):
        # Puedes ajustar los pesos según la estrategia del agente
        return {'feature1': 1.0, 'feature2': 0.5}
    def get_closest_food(self, current_position, food_positions):
        """
        Encuentra la posición de la comida más cercana a la posición actual.
        """
        if not food_positions:
            return None  # No hay comida disponible

        return min(food_positions, key=lambda food: self.manhattan_distance(current_position, food))
    



class OffensiveReflexAgent(ReflexCaptureAgent):
    def get_features(self, game_state, action):
        features = util.Counter()
        successor =  game_state.generate_successor(self.index, action)
        food_list = self.get_food(successor).as_list()

        # Consider the number of food pellets as a feature
        features['num_food'] = -len(food_list)

        if len(food_list) > 0:
            my_pos = successor.get_agent_state(self.index).get_position()
            min_distance = min([self.get_maze_distance(my_pos, food) for food in food_list])
            # Consider the distance to the nearest food pellet as a feature
            features['distance_to_food'] = min_distance

        # Consider the distance to the nearest power capsule as a feature
        capsules = self.get_capsules(successor)
        if capsules:
            min_capsule_distance = min([self.get_maze_distance(my_pos, capsule) for capsule in capsules])
            features['distance_to_capsule'] = min_capsule_distance

        return features
    def get_maze_distance(self, pos1, pos2):
        x1, y1 = pos1
        x2, y2 = pos2
        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
    def get_weights(self, game_state, action):
        return {'successor_score': 100, 'distance_to_food': -1, 'num_food': -10, 'distance_to_capsule': -5}

    def get_food_distance(self, game_state, action):
        successor_state = game_state.generate_successor(self.index, action)
        current_position = game_state.get_agent_position(self.index)
        food_positions = self.get_food(successor_state).as_list()
        closest_food = self.get_closest_food(current_position, food_positions)
        return self.manhattan_distance(current_position, closest_food)

class DefensiveReflexAgent(ReflexCaptureAgent):
    def get_features(self, game_state, action):
        features = {'num_invaders': 0, 'on_defense': 0, 'invader_distance': float('inf'), 'stop': 0, 'reverse': 0, 'closest_enemy_distance': float('inf')}

        my_state = game_state.get_agent_state(self.index)
        my_pos = my_state.get_position()

        enemies = [game_state.get_agent_state(i) for i in self.get_opponents(game_state)]
        invaders = [enemy for enemy in enemies if enemy.is_pacman and enemy.get_position() is not None]

        features['num_invaders'] = len(invaders)

        if len(invaders) > 0:
            dists = [self.get_maze_distance(my_pos, enemy.get_position()) for enemy in invaders if enemy.get_position() is not None]
            features['invader_distance'] = min(dists)

        features['on_defense'] = 1 if not my_state.is_pacman else 0
        features['stop'] = 1 if action == Directions.STOP else 0
        features['reverse'] = 1 if action == Directions.REVERSE[my_state.get_direction()] else 0

        # Consider the distance to the closest enemy as a feature
        for enemy in enemies:
            if enemy.get_position() is not None:
                enemy_distance = self.get_maze_distance(my_pos, enemy.get_position())
                features['closest_enemy_distance'] = min(features['closest_enemy_distance'], enemy_distance)

        return features
    


    def get_weights(self, game_state, action):
        return {'num_invaders': -1000, 'on_defense': 100, 'invader_distance': -10, 'stop': -100, 'reverse': -2, 'closest_enemy_distance': -5}
    
    def get_maze_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def get_num_invaders(self, game_state):
        my_state = game_state.get_agent_state(self.index)
        my_position = my_state.get_position()
        opponents = self.get_opponents(game_state)
        invaders = [game_state.get_agent_state(opp) for opp in opponents if game_state.get_agent_state(opp).is_pacman]

        num_invaders = sum(1 for invader in invaders if self.manhattan_distance(my_position, invader.get_position()) <= 5)
        return num_invaders
