"""
 @author     : Bangqi Wang (bwang.will@gmail.com)
 @file       : winnon_margin.py
 @brief      : Implementation for winnon with margin
"""
import numpy as np
import Queue

class Winnon_Margin(object):
    """docstring for Winnon_margin"""
    def __init__(self, R, x, x_train, x_test, y, y_train, y_test, n, samples, size, loops, alphas, gammas):
        super(Winnon_Margin, self).__init__()
        """ init function:
            1. parse dataset
            2. train
            3. test
            4. count
        """
        # parse x, y entire dataset
        shuffle_size = np.random.permutation(size)
        self.x = x[shuffle_size][:]
        self.y = np.array([y[shuffle_size]]).T
        # parse train & test dataset
        shuffle_samples = np.random.permutation(samples)
        self.x_train = x_train[shuffle_samples][:]
        self.x_test = x_test
        self.y_train = np.array([y_train[shuffle_samples]]).T
        self.y_test = np.array([y_test]).T
        self.theta = -n

        # train
        self.training(alphas, n, samples, loops, gammas)
        if not R:
            # validation
            self.validation(n, size)
        else:
            # count
            self.count(R, n, size)


    def training(self, alphas, n, samples, loops, gammas):
        """ train
            this function tunes the alpha & gamma, and choose the best alpha & gamma from alphas & gammas
        """
        queue = Queue.PriorityQueue()
        # calculate accuracy for each alpha
        for alpha in alphas:
            # calculate accuracy for each gamma
            for gamma in gammas:
                w, mistakes, error = np.ones(n), 0, []
                for loop in range(loops):
                    for i in range(samples):
                        x, y = self.x_train[i], self.y_train[i]
                        # check mistake
                        if (y * (np.dot(w, x) + self.theta))[0] < 0:
                            mistakes += 1
                        # update rules
                        if (y * (np.dot(w, x) + self.theta))[0] <= gamma:
                            w *= np.power(alpha, y*x)
                        if i % 500 == 0:
                            error.append(mistakes)
                # test
                acc = self.evaluation(w, samples)
                print 'alpha = {}, gamma = {}, acc = {}'.format(alpha, gamma, acc)
                queue.put([-acc, alpha, gamma, w, error])
        # choose the best parameters
        self.loss, self.alpha, self.gamma = queue.get()[:3]
        print '===Best===> alpha: {}, gamma: {} -> acc: {}'.format(self.alpha, self.gamma, -self.loss)


    def evaluation(self, w, samples):
        """ evaluate:
            this function calculate the accuracy of test dataset
        """
        prediction = self.theta + np.dot(self.x_test, w)
        for i in range(samples):
            prediction[i] = 1 if prediction[i] >= 0 else -1
        return np.sum(np.equal(prediction.astype(np.int32), self.y_test.flat))/float(samples)


    def validation(self, n, size, loops=1):
        print '===Best===> alpha:{}, gamma:{}'.format(self.alpha, self.gamma)
        self.w, self.mistakes, self.error = np.ones(n), 0, []
        for loop in range(loops):
            for i in range(size):
                # check mistake
                x, y = self.x[i], self.y[i]
                if (y * (np.dot(self.w, x) + self.theta))[0] < 0:
                    self.mistakes += 1
                # updates rules
                if (y * (np.dot(self.w, x) + self.theta))[0] <= self.gamma:
                    self.w *= np.power(self.alpha, y*x)
                if i % 500 == 0:
                    self.error.append(self.mistakes)


    def count(self, R, n, size, loops=1):
        """ validation:
            this function test on entire dataset after tuning alpha & gamma
        """
        print '===count===> Best Parameter: alpha:{}, gamma:{}'.format(self.alpha, self.gamma)
        self.w, self.mistakes, self.correct = np.ones(n), 0, 0
        for loop in range(loops):
            for i in range(size):
                x, y = self.x[i], self.y[i]
                # reset counter if made mistake
                if (y * (np.dot(self.w, x) + self.theta))[0] < 0:
                    self.mistakes += 1
                    self.correct = 0
                # if predict correct R times, return
                else:
                    self.correct += 1
                    if self.correct == R:
                        return
                # update rules
                if (y * (np.dot(self.w, x) + self.theta))[0] <= self.gamma:
                    self.w *= np.power(self.alpha, y*x)
        

