from ..mvcontext.mvcontext import MVContext
from ..lattice import ConceptLattice


class DecisionLatticePredictor:
    def __init__(self, algo='Sofia', L_max=1000):
        self._algo = algo
        self._L_max = L_max

        self._lattice = ConceptLattice()

    def fit(self, X: MVContext, Y):
        self._lattice = ConceptLattice.from_context(X, algo=self._algo, L_max=self._L_max)
        for c_i, c in enumerate(self._lattice.concepts):
            metrics = self.calc_concept_prediction_metrics(c_i, Y)
            c.measures = dict(metrics, **c.measures)

    def predict(self, X: MVContext):
        bottom_concepts, _ = self._lattice.trace_context(X, use_object_indices=True)
        predictions = [self.average_concepts_predictions(bottom_concepts[g_i]) for g_i in range(X.n_objects)]
        return predictions

    @property
    def lattice(self):
        return self._lattice

    def calc_concept_prediction_metrics(self, c_i, Y):
        raise NotImplementedError

    def average_concepts_predictions(self, concepts_i):
        raise NotImplementedError


class DecisionLatticeClassifier(DecisionLatticePredictor):
    def calc_concept_prediction_metrics(self, c_i, Y):
        extent_i = self._lattice.concepts[c_i].extent_i

        classes = sorted(set(Y))
        self._class_names = classes

        def calc_class_probability(class_, extent_i, Y):
            return sum([Y[g_i] == class_ for g_i in extent_i])/len(extent_i) if len(extent_i) > 0 else None

        if len(extent_i) > 0:
            class_probs = [calc_class_probability(class_, extent_i, Y) for class_ in classes]
            max_prob = max(class_probs)
            max_class = [class_ for class_, class_prob in zip(classes, class_probs) if class_prob==max_prob]
            if len(max_class) == 1:
                max_class = max_class[0]
        else:
            class_probs = None
            max_prob = None
            max_class = None
        metrics = {
            'class_probabilities': class_probs,
            'most_probable_class': max_class,
            'maximum_class_probability': max_prob
        }
        return metrics

    def average_concepts_predictions(self, concepts_i):
        probs_per_class = self.average_concepts_class_probabilities(concepts_i)
        max_prob = max(probs_per_class)
        max_class = [class_ for class_, prob in zip(self._class_names, probs_per_class) if prob == max_prob ]
        if len(max_class) == 1:
            max_class = max_class[0]
        return max_class

    def average_concepts_class_probabilities(self, concepts_i):
        predictions = [self._lattice.concepts[c_i].measures['class_probabilities'] for c_i in concepts_i]
        probs_per_class = [sum(row) / len(row) if len(row) > 0 else None for row in zip(*predictions)]  # transpose data
        return probs_per_class

    def predict_proba(self, X: MVContext):
        bottom_concepts, _ = self._lattice.trace_context(X, use_object_indices=True)
        predictions = [self.average_concepts_class_probabilities(bottom_concepts[g_i]) for g_i in range(X.n_objects)]
        return predictions

    @property
    def class_names(self):
        return self._class_names


class DecisionLatticeRegressor(DecisionLatticePredictor):
    def calc_concept_prediction_metrics(self, c_i, Y):
        extent_i = self._lattice.concepts[c_i].extent_i
        metrics = {"mean_y": sum([Y[g_i] for g_i in extent_i])/len(extent_i) if len(extent_i) else None}
        return metrics

    def average_concepts_predictions(self, concepts_i):
        predictions = [self._lattice.concepts[c_i].measures['mean_y'] for c_i in concepts_i]
        avg_prediction = sum(predictions)/len(predictions) if len(predictions) > 0 else None
        return avg_prediction
