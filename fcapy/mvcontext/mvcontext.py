class MVContext:
    """
    A class used to represent Multi Valued Context object from FCA theory.

    """
    def __init__(self, data=None, pattern_types=None, object_names=None, attribute_names=None, **kwargs):
        self._n_objects = len(data) if data is not None else None
        self._n_attributes = len(data[0]) if data is not None else None

        self.object_names = object_names
        self.attribute_names = attribute_names
        self.pattern_structures = self.assemble_pattern_structures(data, pattern_types)
        self.description = kwargs.get('description')

    @property
    def object_names(self):
        return self._object_names

    @object_names.setter
    def object_names(self, value):
        if value is None:
            self._object_names = [str(idx) for idx in range(self._n_objects)] if self._n_objects is not None else None
            return

        assert len(value) == self._n_objects,\
            'MVContext.object_names.setter: Length of new object names should match length of data'
        assert all(type(name) == str for name in value),\
            'MVContext.object_names.setter: Object names should be of type str'
        self._object_names = value

    @property
    def attribute_names(self):
        return self._attribute_names

    @attribute_names.setter
    def attribute_names(self, value):
        if value is None:
            self._attribute_names = [str(idx) for idx in range(self._n_attributes)]\
                if self._n_attributes is not None else None
            return

        assert len(value) == self._n_attributes,\
            'MVContext.attribute_names.setter: Length of "value" should match length of data[0]'
        assert all(type(name) == str for name in value),\
            'MVContext.object_names.setter: Object names should be of type str'
        self._attribute_names = value

    @property
    def pattern_structures(self):
        return self._pattern_structures

    @pattern_structures.setter
    def pattern_structures(self, value):
        self._pattern_structures = value

    def assemble_pattern_structures(self, data, pattern_types):
        if data is None:
            return None

        if pattern_types is not None:
            defined_patterns = set([attr_name for attr_names in pattern_types.keys()
                                    for attr_name in (attr_names if type(attr_names) != str else [attr_names])])
        else:
            defined_patterns = set()
        missed_patterns = set(self._attribute_names) - defined_patterns
        assert len(missed_patterns) == 0,\
            f'MVContext.assemble_pattern_structures error. Patterns are undefined for attributes {missed_patterns}'

        names_to_indexes_map = {m: m_i for m_i, m in enumerate(self._attribute_names)}
        pattern_structures = []
        for name, ps_type in pattern_types.items():
            m_i = names_to_indexes_map[name]
            ps_data = [row[m_i] for row in data]
            ps = ps_type(ps_data, name=name)
            pattern_structures.append(ps)
        return pattern_structures

    def extension_i(self, descriptions_i):
        extent = set(range(self._n_objects))
        for ps_i, description in descriptions_i.items():
            ps = self._pattern_structures[ps_i]
            extent &= set(ps.extension_i(description))
        extent = sorted(extent)
        return extent

    def intention_i(self, object_indexes):
        description_i = {ps_i: ps.intention_i(object_indexes) for ps_i, ps in enumerate(self._pattern_structures)}
        return description_i

    def extension(self, descriptions):
        ps_names_map = {ps.name: ps_i for ps_i, ps in enumerate(self._pattern_structures)}
        descriptions_i = {ps_names_map[ps_name]: description for ps_name, description in descriptions.items()}
        extension_i = self.extension_i(descriptions_i)
        objects = [self._object_names[g_i] for g_i in extension_i]
        return objects

    def intention(self, objects):
        objects = set(objects)
        object_indexes = [g_i for g_i, g in enumerate(self._object_names) if g in objects]
        descriptions_i = self.intention_i(object_indexes)
        description = {self._pattern_structures[ps_i].name: description for ps_i, description in descriptions_i.items()}
        return description

    @property
    def n_objects(self):
        """Get the number of objects in the context (i.e. len(`data`))"""
        return self._n_objects

    @property
    def n_attributes(self):
        """Get the number of attributes in the context (i.e. len(`data[0]`)"""
        return self._n_attributes

    @property
    def description(self):
        """Get or set the human readable description of the context

        JSON is the only file format to store this information.
        The description will be lost when saving context to .cxt or .csv

        Parameters
        ----------
        value : `str, None
            The human readable description of the context

        Raises
        ------
        AssertionError
            If the given ``value`` is not None and not of type `str

        """
        return self._description

    @description.setter
    def description(self, value):
        assert isinstance(value, (type(None), str)), 'FormalContext.description: Description should be of type `str`'

        self._description = value

    def to_json(self, path=None):
        """Convert the FormalContext into json file format (save if ``path`` is given)

        Parameters
        ----------
        path : `str or None
            Path to save a context

        Returns
        -------
        context : `str
            If ``path`` is None, the string with .json file data is returned. If ``path`` is given - return None

        """
        raise NotImplementedError

    def to_csv(self, path=None, **kwargs):
        """Convert the FormalContext into csv file format (save if ``path`` is given)

        Parameters
        ----------
        path : `str or None
            Path to save a context
        **kwargs :
            ``sep`` : `str
                Field delimiter for the output file

        Returns
        -------
        context : `str
            If ``path`` is None, the string with .csv file data is returned. If ``path`` is given - return None

        """
        raise NotImplementedError

    def to_pandas(self):
        """Convert the FormalContext into pandas.DataFrame object

        Returns
        -------
        df : pandas.DataFrame
            The dataframe with boolean variables,
            ``object_names`` turned into ``df.index``, ``attribute_names`` turned into ``df.columns``

        """
        raise NotImplementedError

    @staticmethod
    def from_pandas(dataframe):
        raise NotImplementedError

    def __repr__(self):
        data_to_print = f'MultiValuedContext ' +\
                        f'({self.n_objects} objects, {self.n_attributes} attributes)'
        return data_to_print

    def __eq__(self, other):
        """Wrapper for the comparison method __eq__"""
        if not self.object_names == other.object_names:
            raise ValueError('Two MVContext objects can not be compared since they have different object_names')

        if not self.attribute_names == other.attribute_names:
            raise ValueError('Two MVContext objects can not be compared since they have different attribute_names')

        is_equal = self.pattern_structures == other.pattern_structures
        return is_equal

    def __ne__(self, other):
        """Wrapper for the comparison method __ne__"""
        if not self.object_names == other.object_names:
            raise ValueError('Two MVContext objects can not be compared since they have different object_names')

        if not self.attribute_names == other.attribute_names:
            raise ValueError('Two MVContext objects can not be compared since they have different attribute_names')

        is_not_equal = self.pattern_structures != other.pattern_structures
        return is_not_equal

    def __hash__(self):
        return hash((tuple(self._object_names), tuple(self._attribute_names), tuple(self._pattern_structures)))