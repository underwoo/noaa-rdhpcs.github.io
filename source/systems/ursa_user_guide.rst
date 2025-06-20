.. _ursa-user-guide:

***************
Ursa User Guide
***************

.. image:: /images/Ursa.png
   :scale: 45%

.. _ursa-system-overview:

Ursa System Overview
====================
Ursa is located at the :ref:`NOAA Environmental Security Computing
Center (NESCC) <locations-of-rdhpcs>`, located in Fairmont, West
Virginia.

Getting Started with Ursa
-------------------------
Log into your NOAA Google account, and you can view a
`slide presentation introducing Ursa
<https://docs.google.com/presentation/d/1Miz_d5-atesgbfQhVk7LAWFNiveWwyDQFz3XZ4dfXLg/edit?pli=1&slide=id.p#slide=id.p>`_.
Log into your NOAA Google account, and you can also review
a `recorded version of the presentation
<https://drive.google.com/file/d/15-C4Zs_oMxUQ2_QqPm-9CkxPkeK46q56/view>`_.

Ursa System Configuration
=========================

.. list-table::
   :header-rows: 1
   :stub-columns: 1
   :align: left

   * -
     - Compute System
     - GPU System
   * - CPU Type
     - AMD Genoa 9654: 96 cores/12 channels to memory
     - AMD Genoa 9654: 96 cores/12 channels to memory
   * - CPU Speed (GHz)
     - 2.4 GHz
     - 2.4 GHz
   * - Compute Nodes
     - 576
     - 58
   * - Cores/Node
     - 192
     - 192
   * - Total Cores
     - 110,592
     - 11,136
   * - Memory/Core (GB)
     - 2
     - 2
   * - OS
     - Rocky 9
     - Rocky 9
   * - CPU Peak Performance
     - 4.25 PFlops
     - 0.43 PFlops
   * - Interconnect
     - NDR-200 IB
     - NDR-200 IB
   * - Total Disk Capacity
     - >100 PB, (shared with Hera)
     - >100 PB, (shared with Hera)
   * - Total Ave Disk Performance
     - >1000 GB/s
     - >1000 GB/s
   * - GPU Type
     - N/A
     - NVIDIA H100-NVL
   * - GPU's/node
     - N/A
     - 2
   * - Memory/GPU (GB)
     - N/A
     - 94
   * - Total GPU FLOPS (TFLOPS)
     - N/A
     - 3.48 PFlops

Ursa Partitions
---------------

.. list-table::
   :header-rows: 1
   :stub-columns: 1
   :align: left

   * - Partition
     - QOS Allowed
     - Billing TRES Factor
     - Description
   * - u1-compute
     - batch,windfall, debug, urgent, long
     - 100
     - General compute resource. **Default** if no partition is specified.
   * - u1-h100
     - gpu, gpuwf
     - 100
     - For jobs that require nodes with GPUs.
   * - u1-service
     - batch, windfall
     - 100
     - Serial jobs (max 4 cores), with a 24 hr limit. Jobs will be run on
       service nodes that have external network connectivity. Useful
       for data transfers or access to external resources like databases.
       If your workflow requires pushing or pulling data to/from
       the HSMS(HPSS), it should be run there. This partition
       is also a good choice for doing your compilations and
       builds of your applications and libraries rather than
       doing it on the login nodes.

See the :ref:`Quality of Service (QOS) table <QOS-table>` for more information.

Ursa Node Sharing
-----------------

Jobs requesting less than 192 cores or the equivalent amount
of memory will share the node with other jobs.

With the Ursa ``u1-compute`` partition:

* If you request 1-191 cores for your job
  you will be allocated and charged for the greater of
  the number of cores requested or the amount of memory
  requested in GB divided by 2.
* If you request 192 or greater cores you will be given and charged for whole
  nodes, in multiples of 192 cores. (ex. Request - 193, charged for 384 cores)

Ursa Front Ends and Service Partition
---------------------------------------
Ursa has 15 outward-facing nodes.

* 4 nodes will be (front-end) login/cron nodes interactive use:
    * ``ufe01-ufe04``, total of 768 cores for interactive use.
      See the `Login (Front End) Node Usage Policy <https://docs.rdhpcs.noaa.gov/queue_policy/policies.html#login-node-usage>`_ for important information about using Login nodes.
* 10 nodes will comprise the service partition:
    * 3,840 cores total.
    * Available via Slurm.
    * Target for compilation and data transfer jobs.
    * Target for scrontab jobs (Scrontab is preferred for recurring jobs).
* 1 node is available for ecflow
    * ``uecflow01``

Using GPU Resources on Ursa
===========================
Ursa has 2 H100 GPUs each with 94GB of memory in the ``u1-h100``
partition as indicated in the table above.  This partition
is only accessible from the ``gpu`` and ``gpuwf`` QOSes.

In order to have priority access to the GPU resources you will need to
have a GPU specific project allocation. Please contact your PI
or Portfolio Manager for getting a GPU specific allocation.

All projects with a CPU project allocation on Ursa have
windfall access to the GPU resources, and conversely all users with
GPU specific project allocations have windfall access
to the non-GPU resources.

Using GPU Resources With a GPU allocation
-----------------------------------------

If you have a GPU specific project allocation on Ursa you
can access the GPUs by
submitting to the ``u1-h100`` partition and ``gpu`` QOS as shown in
the example below where 2 H100 GPUs on 1 node are being requested:

.. code-block:: shell

   sbatch -A mygpu_project -p u1-h100 -q gpu -N 1 –-gres=gpu:h100:2 my_ml.job

Using GPU Resources Without a GPU allocation
--------------------------------------------

Users that do not have GPU specific project allocations
on Ursa can access
the GPU resources at windfall priority. Which means users will be able
to submit jobs to the system, but they will only run when the
resources are not being used by projects that do have a GPU
specific project allocation.
This is helpful for users who are in interested in
exploring the GPU resources for their applications. To use the system
in this mode please submit the jobs to the ``u1-h100`` partition and
``gpuwf``
QOS as shown in the example below where 2 H100 GPUs on 1 node are
being requested:

.. code-block:: shell

   sbatch -A mycpu_project -p u1-h100 -q gpuwf -N 1 –-gres=gpu:h100:2 my_ml.job


Ursa Software Stack
-------------------

* Ursa OS is Rocky 9.4, similar to MSU systems (Rocky 9.1)
  whereas Hera/Jet are Rocky 8.
* Module layout is more akin to what you see on MSU
  systems; installed using spack.

  * Please run the ``module spider`` command to see all
    the available modules!

* Compilers: Intel’s oneapi, Nvidia’s nvhpc, and
  AMD’s AOCC compilers are available.
* MPIs: Intel MPI from Intel, HPC-X MPI from Nvidia, and openMPI
  implementations are available.

  * We have seen much better performance and stability with
    HPC-X in our testing of communication intensive benchmarks
    as it is optimized to take advantage of the NDR-200 IB
    network more effectively.

* An Intel stack is in place. Other stacks will be
  considered if requested.

Ursa File Systems
-----------------
* Ursa will only mount the two new HPFS files systems,
  ``/scratch3`` and ``/scratch4``.
* At Ursa’s initial release (GA), Hera will continue to only
  mount ``/scratch[12]``, therefore data transfers between
  ``/scratch[12]`` and ``/scratch[34]`` will need to be via the
  DTN’s using utilities such as rsync/scp or Globus.
* At the next NESCC DT (6/10/25, subject to change),
  Hera will also mount ``/scratch[34]`` to allow easier data
  migration and the running of Hera jobs on the new file
  systems as well as the old file systems.
* Scratch file systems are **NOT** backed up!

.. caution::
   **Data migration deadline:**: The ``/scratch[12]`` file systems
   will be decommissioned in August. Plan to complete your migration to
   the ``/scratch[34]`` file systems no later than **7/31/25**.

Cron and Scrontab Services
--------------------------
On Ursa both ``cron`` and ``scrontab`` services are available.
We strongly recommend using ``scrontab`` instead of ``cron``
whenever possible.  For information on how to use ``scrontab``
please see :ref:`scrontab <rdhpcs_scrontab>`.

Getting Help
=============

For any Ursa or Rhea issue, open a :ref:`help request <getting_help>`.
