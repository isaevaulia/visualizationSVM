from TSNEImplementation import *


class TsneSolver:
    def __init__(self, p=30.0, m_i=500, n_d=2, i_d=50):
        """ Конструктор класса TsneSolver
        Устанавливает параметры t-SNE

        :param p: перплексия
        :param m_i: количество итераций
        :param n_d: новая размерность
        :param i_d: исходная размерность
        """
        self.perplexity = p
        self.max_iteration = m_i
        self.no_dims = n_d
        self.initial_dims = i_d
        self.tsne_error = 0

    def set_params(self, p=30.0, m_i=500, n_d=2, i_d=50):
        """ Метод для установки параметров t-SNE

        :param p: перплексия
        :param m_i: количество итераций
        :param n_d: новая размерность
        :param i_d: исходная размерность
        """
        self.perplexity = p
        self.max_iteration = m_i
        self.no_dims = n_d
        self.initial_dims = i_d


    def reduce_dim(self, data):  # TODO: change to NumPy from begin
        """ Преобразование GlobalData в NumPy.ndarray -> запуск self.tsne

        :param data: объект GlobalData(Data)
        :return: NumPy.ndarray(<строки в файле>*<кол-во итераций>)  TODO: change
        """
        a = []
        # list(GlobalData) == rows in file
        rows_to_clusterize = list(data)
        for i in range(len(rows_to_clusterize)):
            for j in range(len(rows_to_clusterize.__getitem__(i))):
                a.append(rows_to_clusterize.__getitem__(i).__getitem__(j))

        data_numpy_array = np.array(a)
        data_numpy_array = np.reshape(data_numpy_array, (-1, len(rows_to_clusterize.__getitem__(0))))

        result = self.tsne(data_numpy_array)
        return result

    def tsne(self, X=np.array([])):
        """ Here is magic works  # TODO: i will stop it
            Runs t-SNE on the dataset in the NxD array X to reduce its
            dimensionality to no_dims dimensions. The syntaxis of the function is
            `Y = tsne.tsne(X, no_dims, perplexity), where X is an NxD NumPy array.
        """

        # Check inputs
        if isinstance(self.no_dims, float):
            print("Error: array X should have type float.")
            return -1
        if round(self.no_dims) != self.no_dims:
            print("Error: number of dimensions should be an integer.")
            return -1

        # Initialize variables
        X = TSNEWindow.pca(X, self.initial_dims).real
        (n, d) = X.shape
        max_iter = self.max_iteration
        initial_momentum = 0.5
        final_momentum = 0.8
        eta = 500
        min_gain = 0.01
        Y = np.random.randn(n, self.no_dims)
        dY = np.zeros((n, self.no_dims))
        iY = np.zeros((n, self.no_dims))
        gains = np.ones((n, self.no_dims))

        # Compute P-values
        P = TSNEWindow.x2p(X, 1e-5, self.perplexity)
        P = P + np.transpose(P)
        P = P / np.sum(P)
        P = P * 4.  # early exaggeration
        P = np.maximum(P, 1e-12)

        # Подкотовка изображений

        # Run iterations
        for iter in range(max_iter):

            # Compute pairwise affinities
            sum_Y = np.sum(np.square(Y), 1)
            num = -2. * np.dot(Y, Y.T)
            num = 1. / (1. + np.add(np.add(num, sum_Y).T, sum_Y))
            num[range(n), range(n)] = 0.
            Q = num / np.sum(num)
            Q = np.maximum(Q, 1e-12)

            # Compute gradient
            PQ = P - Q
            for i in range(n):
                dY[i, :] = np.sum(np.tile(PQ[:, i] * num[:, i], (self.no_dims, 1)).T * (Y[i, :] - Y), 0)

            # Perform the update
            if iter < 20:
                momentum = initial_momentum
            else:
                momentum = final_momentum
            gains = (gains + 0.2) * ((dY > 0.) != (iY > 0.)) + \
                    (gains * 0.8) * ((dY > 0.) == (iY > 0.))
            gains[gains < min_gain] = min_gain
            iY = momentum * iY - eta * (gains * dY)
            Y = Y + iY
            Y = Y - np.tile(np.mean(Y, 0), (n, 1))

            # Compute current value of cost function
            if (iter + 1) % 10 == 0:
                C = np.sum(P * np.log(P / Q))
                # print("Iteration %d: error is %f" % (iter + 1, C))
                self.tsne_error = C # error saving
            # Stop lying about P-values
            if iter == 100:
                P = P / 4.
        # Return solution
        return Y
