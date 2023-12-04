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

def create_team(firstIndex, secondIndex, isRed,
			   first = 'OffensiveReflexAgent', second = 'DefensiveReflexAgent', num_training=0):
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
  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]


##########
# Agents #
##########
class ReflexCaptureAgent(CaptureAgent):
    def __init__(self, index, time_for_computing=.1):
        super().__init__(index, time_for_computing)
        self.start = None

    def register_initial_state(self, game_state):
        self.start = game_state.get_agent_position(self.index)
        CaptureAgent.register_initial_state(self, game_state)

    def choose_action(self, game_state):
        actions = game_state.get_legal_actions(self.index)

        values = [self.evaluate(self.get_successor(game_state, action)) for action in actions]

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

    def get_successor(self, game_state, action):
        successor = game_state.generate_successor(self.index, action)
        pos = successor.get_agent_state(self.index).get_position()
        if pos != nearestPoint(pos):
            return successor.generate_successor(self.index, action)
        else:
            return successor

    def evaluate(self, game_state):
        features = self.get_features(game_state)
        weights = self.get_weights(game_state)
        return features * weights

    def get_features(self, game_state):
        features = util.Counter()
        successor = self.get_successor(game_state, Directions.STOP)
        features['successor_score'] = self.get_score(successor)
        return features

    def get_weights(self, game_state):
        return {'successor_score': 1.0}


class OffensiveReflexAgent(ReflexCaptureAgent):
    def get_features(self, game_state):
        '''features = util.Counter()
        successor = self.get_successor(game_state, Directions.STOP)
        food_list = self.get_food(successor).as_list()
        features['successor_score'] = -len(food_list)

        my_state = successor.get_agent_state(self.index)
        my_pos = my_state.get_position()

        # Compute distance to the nearest ghost
        enemies = [successor.get_agent_state(i) for i in self.get_opponents(successor)]
        ghosts = [a for a in enemies if not a.is_pacman and a.get_position() is not None]
        if len(ghosts) > 0:
            dists = [self.get_maze_distance(my_pos, a.get_position()) for a in ghosts]
            features['distance_to_ghost'] = min(dists)

        # Check if returning home
        features['returning_home'] = 1 if my_state.is_pacman and my_state.num_carrying > 0 else 0

        if len(food_list) > 0:
            # Prioritize eating food
            min_distance_to_food = min([self.get_maze_distance(my_pos, food) for food in food_list])
            features['distance_to_food'] = min_distance_to_food

            # Penalizar la proximidad a los fantasmas cuando lleva bolas y está volviendo a casa
            if features['returning_home'] and min_distance_to_food > 0:
                features['distance_to_ghost'] /= min_distance_to_food

        return features
        '''
        features = util.Counter()
        successor = self.get_successor(game_state, Directions.STOP)
        food_list = self.get_food(successor).as_list()
        features['successor_score'] = -len(food_list)

        my_state = successor.get_agent_state(self.index)
        my_pos = my_state.get_position()

        # Compute distance to the nearest ghost
        enemies = [successor.get_agent_state(i) for i in self.get_opponents(successor)]
        ghosts = [a for a in enemies if not a.is_pacman and a.get_position() is not None]
        if len(ghosts) > 0:
            dists = [self.get_maze_distance(my_pos, a.get_position()) for a in ghosts]
            features['distance_to_ghost'] = min(dists)

        # Check if returning home
        features['returning_home'] = 1 if my_state.is_pacman and my_state.num_carrying > 0 else 0

        if len(food_list) > 0:
            # Prioritize eating food
            min_distance_to_food = min([self.get_maze_distance(my_pos, food) for food in food_list])
            features['distance_to_food'] = min_distance_to_food

            # Penalizar la proximidad a los fantasmas cuando lleva bolas y está volviendo a casa
            if features['returning_home'] and min_distance_to_food > 0:
                features['distance_to_ghost'] /= min_distance_to_food

        return features

    def get_weights(self, game_state):
        # Ajusta los pesos según tus preferencias y experimentos
        return {'successor_score': 100, 'distance_to_food': -1, 'distance_to_ghost': 10, 'returning_home': 50}
    def choose_action(self, game_state):
        actions = game_state.get_legal_actions(self.index)

        values = [self.evaluate(self.get_successor(game_state, action)) for action in actions]

        max_value = max(values)
        best_actions = [a for a, v in zip(actions, values) if v == max_value]

        food_left = len(self.get_food(game_state).as_list())

        if food_left <= len(self.get_food(game_state).as_list()) / 2:
            # Si tiene la mitad o menos de las bolas blancas, y los oponentes están cerca, retrocede hacia su lado
            enemies = [game_state.get_agent_state(i) for i in self.get_opponents(game_state)]
            invaders = [a for a in enemies if a.is_pacman and a.get_position() is not None]
            if len(invaders) > 0:
                min_distance = min([self.get_maze_distance(game_state.get_agent_state(self.index).get_position(), a.get_position()) for a in invaders])
                if min_distance < 5:  # Ajusta la distancia según sea necesario
                    return Directions.WEST  # Cambia la dirección según sea necesario para retroceder

        # Si no cumple la condición anterior, elige aleatoriamente entre las mejores acciones
        return random.choice(best_actions)


class DefensiveReflexAgent(ReflexCaptureAgent):
    def get_features(self, game_state):
        features = util.Counter()
        successor = self.get_successor(game_state, Directions.STOP)

        my_state = successor.get_agent_state(self.index)
        my_pos = my_state.get_position()

        features['on_defense'] = 1
        if my_state.is_pacman:
            features['on_defense'] = 0

        enemies = [successor.get_agent_state(i) for i in self.get_opponents(successor)]
        invaders = [a for a in enemies if a.is_pacman and a.get_position() is not None]
        features['num_invaders'] = len(invaders)
        if len(invaders) > 0:
            dists = [self.get_maze_distance(my_pos, a.get_position()) for a in invaders]
            features['invader_distance'] = min(dists)
        return features
        '''features = util.Counter()
        successor = self.get_successor(game_state, Directions.STOP)

        my_state = successor.get_agent_state(self.index)
        my_pos = my_state.get_position()

        features['on_defense'] = 1
        if my_state.is_pacman:
            features['on_defense'] = 0

        enemies = [successor.get_agent_state(i) for i in self.get_opponents(successor)]
        invaders = [a for a in enemies if a.is_pacman and a.get_position() is not None]
        features['num_invaders'] = len(invaders)

        if len(invaders) > 0:
            # Priorizar perseguir al Pacman más cercano
            min_distance, closest_invader = min(
                [(self.get_maze_distance(my_pos, a.get_position()), a) for a in invaders],
                key=lambda x: x[0]
            )
            features['invader_distance'] = min_distance

        return features
        '''

    def get_weights(self, game_state):
        return {'num_invaders': -1000, 'on_defense': 100, 'invader_distance': -10}

    def choose_action(self, game_state):
        actions = game_state.get_legal_actions(self.index)

        values = [self.evaluate(self.get_successor(game_state, action)) for action in actions]

        max_value = max(values)
        best_actions = [a for a, v in zip(actions, values) if v == max_value]

        food_left = len(self.get_food(game_state).as_list())

        if food_left <= 2:
            best_dist = float('inf')
            best_action = None
            for action in actions:
                successor = self.get_successor(game_state, action)
                pos2 = successor.get_agent_position(self.index)
                dist = self.get_maze_distance(self.start, pos2)
                if dist < best_dist:
                    best_action = action
                    best_dist = dist
            return best_action

        # Persigue al Pacman más cercano si hay invasores
        enemies = [game_state.get_agent_state(i) for i in self.get_opponents(game_state)]
        invaders = [a for a in enemies if a.is_pacman and a.get_position() is not None]
        if len(invaders) > 0:
            min_distance, closest_invader = min(
                [(self.get_maze_distance(game_state.get_agent_state(self.index).get_position(), a.get_position()), a) for a in invaders],
                key=lambda x: x[0]
            )

            # Obtiene la dirección hacia el Pacman más cercano
            direction_towards_invader = self.get_direction_towards(game_state.get_agent_state(self.index).get_position(), closest_invader.get_position())

            # Verifica si la dirección es legal antes de devolverla
            if direction_towards_invader in actions:
                return direction_towards_invader

        # Si no puede perseguir a un invasor, elige aleatoriamente entre las mejores acciones
        return random.choice(best_actions)
    def get_direction_towards(self, start, goal):
        x1, y1 = start
        x2, y2 = goal

        # Calcula las diferencias en coordenadas
        x_diff = x2 - x1
        y_diff = y2 - y1

        # Determina la dirección en función de las diferencias en coordenadas
        if x_diff > 0:
            return 'East'
        elif x_diff < 0:
            return 'West'
        elif y_diff > 0:
            return 'North'
        elif y_diff < 0:
            return 'South'
        else:
            return 'Stop'
