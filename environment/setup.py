from typing import Collection
from pabutools.utils import powerset
import pabutools.election as pbe

import numpy as np
import random as rand


class Mproject():
    """Mproject means Multi-Project, it is the equivalent class for single dimension PB as defined in the pabutools library
    """
    def __init__(self, name:str, cost:np.ndarray, categories:set[str]=set(), targets:set[str]=set()):
        """Mirrors the pabutools Project class. An object to store details of a project

        Args:
            name (str): The name of the project
            cost (np.array): Project cost
            categories (set[str], optional): Set of categories the project belongs to. Defaults to None.
            targets (set[str], optional): Set of target audience. Defaults to None.
        """
        self.name = name
        self.cost = cost
        self.categories = categories
        self.targets = targets

    def copy(self):
        return Mproject(self.name, self.cost.copy(), self.categories.copy(), self.targets.copy())

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class Minstance(set[Mproject]):
    """Minstance is the multi-instance version for the Instance class in pabutools
    """
    def __init__(self, init:Collection[Mproject]=(), budget_limit=np.array([0]), categories:set[str]=set(), targets:set[str]=set(), name:str = ""):
        """Create the instance to extend a set[Project], so all of the set functions can be used for the Minstance

        Args:
            init (Collection[Mproject], optional): Collection of projects to add to the instance, any with the wrong shaped cost will be removed. Defaults to ().
            budget_limit (_type_, optional): The budget limit as an array. Defaults to np.array([0]).
            categories (set[str], optional): Categories that the instance falls under. Defaults to None.
            targets (set[str], optional): The target voters for the instance. Defaults to None.
        """
        set.__init__(self, init)
        self.budget_limit:np.ndarray = budget_limit
        self.categories = categories
        self.targets = targets
        self.name = name

        # Make sure all projects have correct budget size
        to_remove = []
        for p in self:
            if np.size(p.cost) != np.size(self.budget_limit):
                print(f"{p} has the wrong number of resources, it will be removed from the instance")
                to_remove.append(p)
        for p in to_remove:
            self.remove(p)

    def __str__(self):
        output = '\033[4m' + self.name + '\033[0m' + "\n"
        output += f"Budget: {self.budget_limit}\n"
        output += f"Categories: {self.categories}\n"
        output += f"Targets: {self.targets}\n\n"
        output += "Projects: \n"
        output += "---------------------------\n"
        for p in self:
            output += f"{p.name}\n\tCost: {p.cost}\n\tCategories: {p.categories}\n\tTargets: {p.targets}\n"
            output += "---------------------------\n"
        return output

    def __repr__(self):
        return super().__repr__()

    def copy(self):
        x = super().copy()
        return Minstance(x, self.budget_limit.copy(), self.categories.copy(), self.targets.copy(), self.name)

    def get_project(self, project_name:str) -> Mproject:
        """Retrieve a project from its name, if no project exists returns None

        Args:
            project_name (str): The name of the project to find

        Returns:
            Mproject: The project with the given name
        """
        for p in self:
            if p.name == project_name:
                return p
        return None

    def is_feasible(self, projects:set[Mproject]) -> bool:
        """Returns a bool representing whether a given set of projects is feasible, returns false if some of the projects not in the instance

        Args:
            projects (set[Mproject]): _description_

        Returns:
            bool: _description_
        """
        # Make sure all in instance
        if not projects.issubset(self):
            return False

        # Calculate the total cost of the projects
        total_cost = np.array([0 for i in range(np.size(self.budget_limit))])

        for p in projects:
            total_cost += p.cost

        if min(self.budget_limit - total_cost) < 0:
            return False
        else:
            return True

    def is_exhaustive(self, projects:set[Mproject]) -> bool:
        """Returns true if the set of project is a maximal subset of the instance

        Args:
            projects (set[Mproject]): The set of projects to test

        Returns:
            bool: A bool which is True if the budget is exhausted and False if not or a project is not in the instance
        """

        # Make sure all projects in instance
        if not projects.issubset(self):
            return False

        # Calculate the cost of the projects
        total_cost = np.array([0 for i in range(np.size(self.budget_limit))])

        for p in projects:
            total_cost += p.cost

        remaining = self.budget_limit - total_cost

        # Check if any projects can be funded
        for p in self.symmetric_difference(projects):
            if min(remaining - p.cost) >= 0:
                return False
        return True

    def is_trivial(self) -> bool:
        """Returns a bool saying if the instance is tivial. That is, if all projects can be funded or no projects can be funded

        Returns:
            bool: _description_
        """
        # Can all projects be funded
        if self.is_feasible(self):
            return True

        # If a project can be funded then False will be returned. If not then the instance is trivial
        for p in self:
            if self.is_feasible(set([p])):
                return False
        return True

    def remove_unaffordable_projects(self):
        """ Remove any projects from the instance that cannot be afforded with the given budget

        Args:
            instance (Minstance): The instance
            remaining_budget (np.array): The budget left
        """
        to_remove = set()
        for c in self:
            if min(self.budget_limit - c.cost) < 0:
                to_remove.add(c)

        self.difference_update(to_remove)


def get_random_minstance(num_projects:int, min_cost:np.array, max_cost:np.array, budget:np.array) -> Minstance:
    """Generates a random instance with given budget

    Args:
        num_projects (int): The number of projects to generate
        min_cost (np.array): Minimum cost of the projects
        max_cost (np.array): Maximum cost of the projects
        budget (np.array): The budget for the instance


    Returns:
        Minstance: The random instance
    """
    if np.size(min_cost) != np.size(budget) or np.size(max_cost) != np.size(budget):
        return None
    else:
        # Create list of random projects
        num_resources = np.size(budget)
        projects = []
        for i in range(num_projects):
            cost = np.array([rand.randint(min_cost[j], max_cost[j]) for j in range(num_resources)])
            projects.append(Mproject(f"Project {i}", cost))

        # Create the instance
        return Minstance(projects, budget, name=f"Random Instance")

def get_voters_for_project(c, profile:pbe.ApprovalProfile) -> list[int]:
    """Returns the indexes of voters in the profile for which they approve of project c

    Args:
        c (Mproject): The project in question
        profile (pbe.ApprovalProfile): The profile

    Returns:
        list[int]: List of indexes of voters in the profile
    """
    voters = []
    for i in range(len(profile)):
        if c in profile[i]:
            voters.append(i)

    return voters
