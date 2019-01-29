
# coding: utf-8

# In[28]:


import gym
import random
import torch
import numpy as np
from collections import deque
import matplotlib.pyplot as plt
from agents.q_learner import Q_learner
from agents.distrib_learner import Distrib_learner
import matplotlib.pyplot as plt
plt.rcdefaults()

# In[30]:


args = dict()
args["BUFFER_SIZE"] = int(500)  # replay buffer size
args["BATCH_SIZE"] = 32  # minibatch size
args["GAMMA"] = 0.95  # discount factor
args["TAU"] = 1e-3  # for soft update of target parameters
args["LR"] = 3e-4  # learning rate
args["UPDATE_EVERY"] = 4  # how often to update the network


# In[31]:
N = 10
Vmin = 0
Vmax = 200
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

env = gym.make('CartPole-v1')
env.seed(0)
agent = Distrib_learner(N=N, Vmin=Vmin, Vmax=Vmax, state_size=env.observation_space.shape[0], action_size= env.action_space.n, seed=0, hiddens = [24,24], args = args)


# In[32]:


def dqn(n_episodes=10000, max_t=1000, eps_start=0.1, eps_end=0.02, eps_decay=0.995):

    scores = []                        # list containing scores from each episode
    scores_window = deque(maxlen=100)  # last 100 scores
    eps = eps_start                    # initialize epsilon
    for i_episode in range(1, n_episodes+1):
        state = env.reset()
        score = 0
        for t in range(max_t):
            action = agent.act(state, eps)
            next_state, reward, done, _ = env.step(action)
            agent.step(state, action, reward, next_state, done)

            state = next_state
            score += reward
            if done:
                break 
        scores_window.append(score)       # save most recent score
        scores.append(score)              # save most recent score
        eps = max(eps_end, eps_decay*eps) # decrease epsilon
        
        print('\rEpisode {}\tAverage Score: {:.2f}'.format(i_episode, np.mean(scores_window)), end="")
        if i_episode % 100 == 0:
            state = torch.from_numpy(state).float().unsqueeze(0).to(device)
            q_distrib = agent.qnetwork_local.forward(state).detach()
            q_distrib = q_distrib.view(-1, N, env.action_space.n)[0]
            delta_z = (Vmax - Vmin) / (N - 1)
            y = np.arange(Vmin, Vmax + delta_z,delta_z )

            for i in range(env.action_space.n):
                z = q_distrib[:,i].cpu().data.numpy()
                print(z.shape)
                print(y.shape)
                plt.bar(y, z, width = 10)

            plt.show()
            print('\rEpisode {}\tAverage Score: {:.2f}'.format(i_episode, np.mean(scores_window)))
        if np.mean(scores_window)>=200.0:
            print('\nEnvironment solved in {:d} episodes!\tAverage Score: {:.2f}'.format(i_episode-100, np.mean(scores_window)))
            torch.save(agent.qnetwork_local.state_dict(), 'models/checkpoints/checkpoint.pth')
            break
    return scores

scores = dqn()

# plot the scores
fig = plt.figure()
ax = fig.add_subplot(111)
plt.plot(np.arange(len(scores)), scores)
plt.ylabel('Score')
plt.xlabel('Episode #')
plt.show()

