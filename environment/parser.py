import csv
import pabutools.election as pbe

from setup import *
import numpy as np
import random as rand

def parse(path, num_resources=1, random_budget=False):

    with open(path, 'r', newline='', encoding="utf-8") as csvfile:
        meta = {}
        projects = {}
        votes = {}
        section = ""
        header = []
        reader = csv.reader(csvfile, delimiter=';')
        for row in reader:
            if str(row[0]).strip().lower() in ["meta", "projects", "votes"]:
                section = str(row[0]).strip().lower()
                header = next(reader)
            elif section == "meta":
                meta[row[0]] = row[1].strip()
            elif section == "projects":
                projects[row[0]] = {}
                for it, key in enumerate(header[1:]):
                    projects[row[0]][key.strip()] = row[it+1].strip()
            elif section == "votes":
                votes[row[0]] = {}
                for it, key in enumerate(header[1:]):
                    votes[row[0]][key.strip()] = row[it+1].strip()

    b = float(meta['budget'])
    if num_resources == 1:
        project_list = []
        for i in projects:
            project_list.append(Mproject(i, np.array([float(projects[i]['cost'])])))

        instance = Minstance(project_list, np.array([b]), name=path)
    else: # Currently just num resources is 2
        if not random_budget:
            budget_split = np.array([b/2,b/2])

            project_list = []
            for i in projects:
                # Select a random number between 0 and 1. Split the cost between the two resources. (c*a,c*(1-a))
                cost = float(projects[i]['cost'])
                cost_split = rand.uniform(0, 1)
                project_list.append(Mproject(i,np.array([cost*cost_split, cost*(1-cost_split)])))
            instance = Minstance(project_list, budget_split, name=path)

    ballots = []
    for i in votes:
        p:str = votes[i]['vote']
        p_split = p.split(",")

        b = pbe.ApprovalBallot()
        for name in p_split:
            b.add(instance.get_project(name))

        ballots.append(b)

    profile = pbe.ApprovalProfile(init=ballots, instance=instance)

    return (instance, profile)
