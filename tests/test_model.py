#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014-2020 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#     Santiago Dueñas <sduenas@bitergia.com>
#     Miguel Ángel Fernández <mafesan@bitergia.com>
#

import datetime
import dateutil
import json

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TransactionTestCase

from grimoirelab_toolkit.datetime import datetime_utcnow

from sortinghat.core.models import (Organization,
                                    Domain,
                                    Country,
                                    Individual,
                                    Identity,
                                    Profile,
                                    Enrollment,
                                    MatchingBlacklist,
                                    Transaction,
                                    Operation)

# Test check errors messages
DUPLICATE_CHECK_ERROR = "Duplicate entry .+"
NULL_VALUE_CHECK_ERROR = "Column .+ cannot be null"
INVALID_BOOLEAN_CHECK_ERROR = "['“true” value must be either True or False.']"


class TestOrganization(TransactionTestCase):
    """Unit tests for Organization class"""

    def test_unique_organizations(self):
        """Check whether organizations name are unique"""

        with self.assertRaises(IntegrityError):
            Organization.objects.create(name="Example")
            Organization.objects.create(name="Example")

    def test_charset(self):
        """Check encoding charset"""

        # With an invalid encoding both names wouldn't be inserted;
        # In MySQL, chars 'ı' and 'i' are considered the same with a
        # collation distinct to <charset>_unicode_ci
        Organization.objects.create(name='ıCompany')
        Organization.objects.create(name='iCompany')

        org1 = Organization.objects.get(name='ıCompany')
        org2 = Organization.objects.get(name='iCompany')

        self.assertEqual(org1.name, 'ıCompany')
        self.assertEqual(org2.name, 'iCompany')

    def test_created_at(self):
        """Check creation date is only set when the object is created"""

        before_dt = datetime_utcnow()
        org = Organization.objects.create(name='ıCompany')
        after_dt = datetime_utcnow()

        self.assertGreaterEqual(org.created_at, before_dt)
        self.assertLessEqual(org.created_at, after_dt)

        org.save()

        self.assertGreaterEqual(org.created_at, before_dt)
        self.assertLessEqual(org.created_at, after_dt)

    def test_last_modified(self):
        """Check last modification date is set when the object is updated"""

        before_dt = datetime_utcnow()
        org = Organization.objects.create(name='ıCompany')
        after_dt = datetime_utcnow()

        self.assertGreaterEqual(org.last_modified, before_dt)
        self.assertLessEqual(org.last_modified, after_dt)

        before_modified_dt = datetime_utcnow()
        org.save()
        after_modified_dt = datetime_utcnow()

        self.assertGreaterEqual(org.last_modified, before_modified_dt)
        self.assertLessEqual(org.last_modified, after_modified_dt)


class TestDomain(TransactionTestCase):
    """Unit tests for Domain class"""

    def test_unique_domains(self):
        """Check whether domains are unique"""

        with self.assertRaisesRegex(IntegrityError, DUPLICATE_CHECK_ERROR):
            org = Organization.objects.create(name='Example')
            Domain.objects.create(domain='example.com', organization=org)
            Domain.objects.create(domain='example.com', organization=org)

    def test_not_null_organizations(self):
        """Check whether every domain is assigned to an organization"""

        with self.assertRaisesRegex(IntegrityError, NULL_VALUE_CHECK_ERROR):
            Domain.objects.create(domain='example.com')

    def test_is_top_domain_invalid_type(self):
        """Check invalid values on is_top_domain bool column"""

        with self.assertRaisesRegex(ValidationError, INVALID_BOOLEAN_CHECK_ERROR):
            org = Organization.objects.create(name='Example')
            Domain.objects.create(domain='example.com', is_top_domain='true',
                                  organization=org)

    def test_created_at(self):
        """Check creation date is only set when the object is created"""

        before_dt = datetime_utcnow()
        org = Organization.objects.create(name='Example')
        dom = Domain.objects.create(domain='example.com', is_top_domain=True,
                                    organization=org)
        after_dt = datetime_utcnow()

        self.assertEqual(dom.is_top_domain, True)
        self.assertGreaterEqual(dom.created_at, before_dt)
        self.assertLessEqual(dom.created_at, after_dt)

        dom.is_top_domain = False
        dom.save()

        self.assertEqual(dom.is_top_domain, False)
        self.assertGreaterEqual(dom.created_at, before_dt)
        self.assertLessEqual(dom.created_at, after_dt)

    def test_last_modified(self):
        """Check last modification date is set when the object is updated"""

        before_dt = datetime_utcnow()
        org = Organization.objects.create(name='Example')
        dom = Domain.objects.create(domain='example.com', is_top_domain=True,
                                    organization=org)
        after_dt = datetime_utcnow()

        self.assertEqual(dom.is_top_domain, True)
        self.assertGreaterEqual(dom.last_modified, before_dt)
        self.assertLessEqual(dom.last_modified, after_dt)

        before_modified_dt = datetime_utcnow()
        dom.is_top_domain = False
        dom.save()
        after_modified_dt = datetime_utcnow()

        self.assertEqual(dom.is_top_domain, False)
        self.assertGreaterEqual(dom.last_modified, before_modified_dt)
        self.assertLessEqual(dom.last_modified, after_modified_dt)


class TestCountry(TransactionTestCase):
    """Unit tests for Country class"""

    def test_unique_countries(self):
        """Check whether countries are unique"""

        with self.assertRaisesRegex(IntegrityError, DUPLICATE_CHECK_ERROR):
            Country.objects.create(code='ES', name='Spain', alpha3='ESP')
            Country.objects.create(code='ES', name='España', alpha3='E')

    def test_unique_alpha3(self):
        """Check whether alpha3 codes are unique"""

        with self.assertRaisesRegex(IntegrityError, DUPLICATE_CHECK_ERROR):
            Country.objects.create(code='ES', name='Spain', alpha3='ESP')
            Country.objects.create(code='E', name='Spain', alpha3='ESP')

    def test_created_at(self):
        """Check creation date is only set when the object is created"""

        before_dt = datetime_utcnow()
        country = Country.objects.create(code='ES', name='Spain', alpha3='ESP')
        after_dt = datetime_utcnow()

        self.assertEqual(country.name, 'Spain')
        self.assertGreaterEqual(country.created_at, before_dt)
        self.assertLessEqual(country.created_at, after_dt)

        country.name = 'España'
        country.save()

        self.assertEqual(country.name, 'España')
        self.assertGreaterEqual(country.created_at, before_dt)
        self.assertLessEqual(country.created_at, after_dt)

    def test_last_modified(self):
        """Check last modification date is set when the object is updated"""

        before_dt = datetime_utcnow()
        country = Country.objects.create(code='ES', name='Spain', alpha3='ESP')
        after_dt = datetime_utcnow()

        self.assertEqual(country.name, 'Spain')
        self.assertGreaterEqual(country.last_modified, before_dt)
        self.assertLessEqual(country.last_modified, after_dt)

        before_modified_dt = datetime_utcnow()
        country.name = 'España'
        country.save()
        after_modified_dt = datetime_utcnow()

        self.assertEqual(country.name, 'España')
        self.assertGreaterEqual(country.last_modified, before_modified_dt)
        self.assertLessEqual(country.last_modified, after_modified_dt)


class TestIndividual(TransactionTestCase):
    """Unit tests for Individual class"""

    def test_unique_main_key(self):
        """Check whether the mk is in fact unique"""

        with self.assertRaisesRegex(IntegrityError, DUPLICATE_CHECK_ERROR):
            Individual.objects.create(mk='AAAA')
            Individual.objects.create(mk='AAAA')

    def test_created_at(self):
        """Check creation date is only set when the object is created"""

        before_dt = datetime_utcnow()
        indv = Individual.objects.create(mk='AAAA')
        after_dt = datetime_utcnow()

        self.assertGreaterEqual(indv.created_at, before_dt)
        self.assertLessEqual(indv.created_at, after_dt)

        indv.save()

        self.assertGreaterEqual(indv.created_at, before_dt)
        self.assertLessEqual(indv.created_at, after_dt)

    def test_last_modified(self):
        """Check last modification date is set when the object is updated"""

        before_dt = datetime_utcnow()
        indv = Individual.objects.create(mk='AAAA')
        after_dt = datetime_utcnow()

        self.assertGreaterEqual(indv.last_modified, before_dt)
        self.assertLessEqual(indv.last_modified, after_dt)

        before_modified_dt = datetime_utcnow()
        indv.save()
        after_modified_dt = datetime_utcnow()

        self.assertGreaterEqual(indv.last_modified, before_modified_dt)
        self.assertLessEqual(indv.last_modified, after_modified_dt)

    def test_is_locked_default(self):
        """Check if `is_locked` field is set to False by default"""

        indv = Individual.objects.create(mk='AAAA')

        self.assertEqual(indv.is_locked, False)


class TestIdentity(TransactionTestCase):
    """Unit tests for Identity class"""

    def test_not_null_source(self):
        """Check whether every identity has a source"""

        with self.assertRaisesRegex(IntegrityError, NULL_VALUE_CHECK_ERROR):
            indv = Individual.objects.create(mk='AAAA')
            Identity.objects.create(individual=indv, source=None)

    def test_identities_are_unique(self):
        """Check if there is only one tuple with the same values"""

        indv = Individual.objects.create(mk='AAAA')
        id1 = Identity.objects.create(uuid='A',
                                      name='John Smith',
                                      email='jsmith@example.com',
                                      username='jsmith',
                                      source='scm',
                                      individual=indv)

        with self.assertRaisesRegex(IntegrityError, DUPLICATE_CHECK_ERROR):
            Identity.objects.create(uuid='B',
                                    name='John Smith',
                                    email='jsmith@example.com',
                                    username='jsmith',
                                    source='scm',
                                    individual=indv)

        # Changing an property should not raise any error
        id2 = Identity.objects.create(uuid='B',
                                      name='John Smith',
                                      email='jsmith@example.com',
                                      username='jsmith',
                                      source='mls',
                                      individual=indv)

        self.assertNotEqual(id1.uuid, id2.uuid)

    def test_charset(self):
        """Check encoding charset"""

        # With an invalid encoding both names wouldn't be inserted;
        # In MySQL, chars 'ı' and 'i' are considered the same with a
        # collation distinct to <charset>_unicode_ci
        indv = Individual.objects.create(mk='AAAA')
        Identity.objects.create(uuid='A',
                                name='John Smıth',
                                email='jsmith@example.com',
                                username='jsmith',
                                source='scm',
                                individual=indv)
        Identity.objects.create(uuid='B',
                                name='John Smith',
                                email='jsmith@example.com',
                                username='jsmith',
                                source='scm',
                                individual=indv)

        id1 = Identity.objects.get(name='John Smıth')
        id2 = Identity.objects.get(name='John Smith')

        self.assertEqual(id1.name, 'John Smıth')
        self.assertEqual(id2.name, 'John Smith')

    def test_created_at(self):
        """Check creation date is only set when the object is created"""

        before_dt = datetime_utcnow()
        indv = Individual.objects.create(mk='AAAA')
        id1 = Identity.objects.create(uuid='A',
                                      name='John Smith',
                                      email='jsmith@example.com',
                                      username='jsmith',
                                      source='scm',
                                      individual=indv)
        after_dt = datetime_utcnow()

        self.assertEqual(id1.source, 'scm')
        self.assertGreaterEqual(id1.created_at, before_dt)
        self.assertLessEqual(id1.created_at, after_dt)

        id1.source = 'mls'
        id1.save()

        self.assertEqual(id1.source, 'mls')
        self.assertGreaterEqual(id1.created_at, before_dt)
        self.assertLessEqual(id1.created_at, after_dt)

    def test_last_modified(self):
        """Check last modification date is set when the object is updated"""

        before_dt = datetime_utcnow()
        indv = Individual.objects.create(mk='AAAA')
        id1 = Identity.objects.create(uuid='A',
                                      name='John Smith',
                                      email='jsmith@example.com',
                                      username='jsmith',
                                      source='scm',
                                      individual=indv)
        after_dt = datetime_utcnow()

        self.assertEqual(id1.source, 'scm')
        self.assertGreaterEqual(id1.last_modified, before_dt)
        self.assertLessEqual(id1.last_modified, after_dt)

        before_modified_dt = datetime_utcnow()
        id1.source = 'mls'
        id1.save()
        after_modified_dt = datetime_utcnow()

        self.assertEqual(id1.source, 'mls')
        self.assertGreaterEqual(id1.last_modified, before_modified_dt)
        self.assertLessEqual(id1.last_modified, after_modified_dt)


class TestProfile(TransactionTestCase):
    """Unit tests for Profile class"""

    def test_unique_profile(self):
        """Check if there is only one profile for each individual"""

        indv = Individual.objects.create(mk='AAAA')

        with self.assertRaisesRegex(IntegrityError, DUPLICATE_CHECK_ERROR):
            Profile.objects.create(name='John Smith', individual=indv)
            Profile.objects.create(name='Smith, J.', individual=indv)

    def test_is_bot_invalid_type(self):
        """Check invalid values on is_bot bool column."""

        indv = Individual.objects.create(mk='AAAA')

        with self.assertRaisesRegex(ValidationError, INVALID_BOOLEAN_CHECK_ERROR):
            Profile.objects.create(is_bot='true', individual=indv)

    def test_created_at(self):
        """Check creation date is only set when the object is created"""

        before_dt = datetime_utcnow()
        indv = Individual.objects.create(mk='AAAA')
        prf = Profile.objects.create(name='John Smith', individual=indv)
        after_dt = datetime_utcnow()

        self.assertEqual(prf.name, 'John Smith')
        self.assertGreaterEqual(prf.created_at, before_dt)
        self.assertLessEqual(prf.created_at, after_dt)

        prf.name = 'J. Smith'
        prf.save()

        self.assertEqual(prf.name, 'J. Smith')
        self.assertGreaterEqual(prf.created_at, before_dt)
        self.assertLessEqual(prf.created_at, after_dt)

    def test_last_modified(self):
        """Check last modification date is set when the object is updated"""

        before_dt = datetime_utcnow()
        indv = Individual.objects.create(mk='AAAA')
        prf = Profile.objects.create(name='John Smith', individual=indv)
        after_dt = datetime_utcnow()

        self.assertEqual(prf.name, 'John Smith')
        self.assertGreaterEqual(prf.last_modified, before_dt)
        self.assertLessEqual(prf.last_modified, after_dt)

        before_modified_dt = datetime_utcnow()
        prf.name = 'J. Smith'
        prf.save()
        after_modified_dt = datetime_utcnow()

        self.assertEqual(prf.name, 'J. Smith')
        self.assertGreaterEqual(prf.last_modified, before_modified_dt)
        self.assertLessEqual(prf.last_modified, after_modified_dt)


class TestEnrollment(TransactionTestCase):
    """Unit tests for Enrollment class"""

    def test_not_null_relationships(self):
        """Check whether every enrollment is assigned organizations and individuals"""

        with self.assertRaisesRegex(IntegrityError, NULL_VALUE_CHECK_ERROR):
            Enrollment.objects.create()

        with self.assertRaisesRegex(IntegrityError, NULL_VALUE_CHECK_ERROR):
            indv = Individual.objects.create(mk='AAAA')
            Enrollment.objects.create(individual=indv)

        with self.assertRaisesRegex(IntegrityError, NULL_VALUE_CHECK_ERROR):
            org = Organization.objects.create(name='Example')
            Enrollment.objects.create(organization=org)

    def test_unique_enrollments(self):
        """Check if there is only one tuple with the same values"""

        with self.assertRaisesRegex(IntegrityError, DUPLICATE_CHECK_ERROR):
            indv = Individual.objects.create(mk='AAAA')
            org = Organization.objects.create(name='Example')

            Enrollment.objects.create(individual=indv, organization=org)
            Enrollment.objects.create(individual=indv, organization=org)

    def test_default_enrollment_period(self):
        """Check whether the default period is set when initializing the class"""

        indv = Individual.objects.create(mk='AAAA')
        org = Organization.objects.create(name='Example')

        rol1 = Enrollment.objects.create(individual=indv, organization=org)
        self.assertEqual(rol1.start, datetime.datetime(1900, 1, 1, 0, 0, 0,
                                                       tzinfo=dateutil.tz.tzutc()))
        self.assertEqual(rol1.end, datetime.datetime(2100, 1, 1, 0, 0, 0,
                                                     tzinfo=dateutil.tz.tzutc()))

        rol2 = Enrollment.objects.create(individual=indv, organization=org,
                                         end=datetime.datetime(2222, 1, 1, 0, 0, 0,
                                                               tzinfo=dateutil.tz.tzutc()))
        self.assertEqual(rol2.start, datetime.datetime(1900, 1, 1, 0, 0, 0,
                                                       tzinfo=dateutil.tz.tzutc()))
        self.assertEqual(rol2.end, datetime.datetime(2222, 1, 1, 0, 0, 0,
                                                     tzinfo=dateutil.tz.tzutc()))

        rol3 = Enrollment.objects.create(individual=indv, organization=org,
                                         start=datetime.datetime(1999, 1, 1, 0, 0, 0,
                                                                 tzinfo=dateutil.tz.tzutc()))
        self.assertEqual(rol3.start, datetime.datetime(1999, 1, 1, 0, 0, 0,
                                                       tzinfo=dateutil.tz.tzutc()))
        self.assertEqual(rol3.end, datetime.datetime(2100, 1, 1, 0, 0, 0,
                                                     tzinfo=dateutil.tz.tzutc()))

    def test_created_at(self):
        """Check creation date is only set when the object is created"""

        before_dt = datetime_utcnow()
        indv = Individual.objects.create(mk='AAAA')
        org = Organization.objects.create(name='Example')
        rol = Enrollment.objects.create(individual=indv, organization=org)
        after_dt = datetime_utcnow()

        self.assertEqual(rol.start, datetime.datetime(1900, 1, 1, 0, 0, 0,
                                                      tzinfo=dateutil.tz.tzutc()))
        self.assertGreaterEqual(rol.created_at, before_dt)
        self.assertLessEqual(rol.created_at, after_dt)

        rol.start = datetime.datetime(2001, 1, 1, 0, 0, 0,
                                      tzinfo=dateutil.tz.tzutc())
        rol.save()

        self.assertEqual(rol.start, datetime.datetime(2001, 1, 1, 0, 0, 0,
                                                      tzinfo=dateutil.tz.tzutc()))
        self.assertGreaterEqual(rol.created_at, before_dt)
        self.assertLessEqual(rol.created_at, after_dt)

    def test_last_modified(self):
        """Check last modification date is set when the object is updated"""

        before_dt = datetime_utcnow()
        indv = Individual.objects.create(mk='AAAA')
        org = Organization.objects.create(name='Example')
        rol = Enrollment.objects.create(individual=indv, organization=org)
        after_dt = datetime_utcnow()

        self.assertEqual(rol.start, datetime.datetime(1900, 1, 1, 0, 0, 0,
                                                      tzinfo=dateutil.tz.tzutc()))
        self.assertGreaterEqual(rol.last_modified, before_dt)
        self.assertLessEqual(rol.last_modified, after_dt)

        before_modified_dt = datetime_utcnow()
        rol.start = datetime.datetime(2001, 1, 1, 0, 0, 0,
                                      tzinfo=dateutil.tz.tzutc())
        rol.save()
        after_modified_dt = datetime_utcnow()

        self.assertEqual(rol.start, datetime.datetime(2001, 1, 1, 0, 0, 0,
                                                      tzinfo=dateutil.tz.tzutc()))
        self.assertGreaterEqual(rol.last_modified, before_modified_dt)
        self.assertLessEqual(rol.last_modified, after_modified_dt)


class TestMatchingBlacklist(TransactionTestCase):
    """Unit tests for MatchingBlacklist class"""

    def test_unique_excluded(self):
        """Check whether the excluded term is in fact unique"""

        with self.assertRaisesRegex(IntegrityError, DUPLICATE_CHECK_ERROR):
            MatchingBlacklist.objects.create(excluded='John Smith')
            MatchingBlacklist.objects.create(excluded='John Smith')

    def test_created_at(self):
        """Check creation date is only set when the object is created."""

        before_dt = datetime_utcnow()
        mb = MatchingBlacklist.objects.create(excluded='John Smith')
        after_dt = datetime_utcnow()

        self.assertEqual(mb.excluded, 'John Smith')
        self.assertGreaterEqual(mb.created_at, before_dt)
        self.assertLessEqual(mb.created_at, after_dt)

        mb.excluded = 'J. Smith'
        mb.save()

        self.assertEqual(mb.excluded, 'J. Smith')
        self.assertGreaterEqual(mb.created_at, before_dt)
        self.assertLessEqual(mb.created_at, after_dt)

    def test_last_modified(self):
        """Check last modification date is set when the object is updated"""

        before_dt = datetime_utcnow()
        mb = MatchingBlacklist.objects.create(excluded='John Smith')
        after_dt = datetime_utcnow()

        self.assertEqual(mb.excluded, 'John Smith')
        self.assertGreaterEqual(mb.last_modified, before_dt)
        self.assertLessEqual(mb.last_modified, after_dt)

        before_modified_dt = datetime_utcnow()
        mb.excluded = 'J. Smith'
        mb.save()
        after_modified_dt = datetime_utcnow()

        self.assertEqual(mb.excluded, 'J. Smith')
        self.assertGreaterEqual(mb.last_modified, before_modified_dt)
        self.assertLessEqual(mb.last_modified, after_modified_dt)


class TestTransaction(TransactionTestCase):
    """Unit tests for Transaction class"""

    def test_unique_transactions(self):
        """Check whether transactions are unique"""

        with self.assertRaisesRegex(IntegrityError, DUPLICATE_CHECK_ERROR):
            timestamp = datetime_utcnow()
            Transaction.objects.create(tuid='12345abcd',
                                       name='test',
                                       created_at=timestamp,
                                       authored_by='username')
            Transaction.objects.create(tuid='12345abcd',
                                       name='test',
                                       created_at=timestamp,
                                       authored_by='username')

    def test_created_at(self):
        """Check creation date is only set when the object is created"""

        before_dt = datetime_utcnow()
        trx = Transaction.objects.create(tuid='12345abcd',
                                         name='test',
                                         created_at=datetime_utcnow(),
                                         authored_by='username')
        after_dt = datetime_utcnow()

        self.assertGreaterEqual(trx.created_at, before_dt)
        self.assertLessEqual(trx.created_at, after_dt)

        trx.save()

        # Check if creation date does not change after saving the object
        self.assertGreaterEqual(trx.created_at, before_dt)
        self.assertLessEqual(trx.created_at, after_dt)


class TestOperation(TransactionTestCase):
    """Unit tests for Operation class"""

    def setUp(self):
        """Load initial dataset"""

        Transaction.objects.create(tuid='0123456789abcdef',
                                   name='test', created_at=datetime_utcnow())

    def test_unique_operation(self):
        """Check whether contexts are unique"""

        timestamp = datetime_utcnow()
        trx = Transaction.objects.get(tuid='0123456789abcdef')
        args = json.dumps({'test': 'test_value'})

        with self.assertRaisesRegex(IntegrityError, DUPLICATE_CHECK_ERROR):
            Operation.objects.create(ouid='12345abcd', op_type=Operation.OpType.ADD,
                                     entity_type='individual', target='test',
                                     timestamp=timestamp, args=args, trx=trx)
            Operation.objects.create(ouid='12345abcd', op_type=Operation.OpType.ADD,
                                     entity_type='individual', target='test',
                                     timestamp=timestamp, args=args, trx=trx)

    def test_created_at(self):
        """Check creation date is only set when the object is created"""

        trx = Transaction.objects.get(tuid='0123456789abcdef')
        args = json.dumps({'test': 'test_value'})

        before_dt = datetime_utcnow()
        operation = Operation.objects.create(ouid='12345abcd', op_type=Operation.OpType.ADD,
                                             entity_type='individual', target='test',
                                             timestamp=datetime_utcnow(), args=args, trx=trx)
        after_dt = datetime_utcnow()

        self.assertGreaterEqual(operation.timestamp, before_dt)
        self.assertLessEqual(operation.timestamp, after_dt)

        operation.save()

        # Check if timestamp does not change after saving the object
        self.assertGreaterEqual(operation.timestamp, before_dt)
        self.assertLessEqual(operation.timestamp, after_dt)

    def test_invalid_operation_type_none(self):
        """Check if an error is raised when the operation type is `None`"""

        trx = Transaction.objects.get(tuid='0123456789abcdef')
        args = json.dumps({'test': 'test_value'})

        with self.assertRaisesRegex(IntegrityError, NULL_VALUE_CHECK_ERROR):
            Operation.objects.create(ouid='12345abcd', op_type=None,
                                     entity_type='individual', target='test-target',
                                     timestamp=datetime_utcnow(), args=args, trx=trx)

    def test_empty_args(self):
        """Check if an error is raised when no args are set"""

        trx = Transaction.objects.get(tuid='0123456789abcdef')

        with self.assertRaisesRegex(IntegrityError, NULL_VALUE_CHECK_ERROR):
            Operation.objects.create(ouid='12345abcd', op_type=Operation.OpType.ADD,
                                     entity_type='individual', target='test',
                                     timestamp=datetime_utcnow(), args=None, trx=trx)
